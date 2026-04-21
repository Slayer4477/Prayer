#!/usr/bin/env python3
"""
Namoz Vaqtlari v4
• Hozirgi soat (o'ng tomonda)
• Mini rejim (faqat qolgan vaqt)
• Sozlamalar tugmasi: shaffoflik, har doim ustda, va boshqalar
• aladhan.com API + ISLOM.uz moslik (Method 3 + Hanafi)
Talablar: pip install pygame numpy
"""

import tkinter as tk
from tkinter import Canvas, ttk
import datetime, threading, sys, os, json
import urllib.request, urllib.parse

# ─── Papka ────────────────────────────────────────────────────────────────────
DIR         = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(DIR, "config.json")
CACHE_FILE  = os.path.join(DIR, "times_cache.json")
MONTH_CACHE = os.path.join(DIR, "month_cache.json")

# ─── O'zbekiston shaharlari ───────────────────────────────────────────────────
UZB_CITIES = {
    "Toshkent":  (41.2995, 69.2401),
    "Samarqand": (39.6542, 66.9597),
    "Buxoro":    (39.7747, 64.4286),
    "Namangan":  (41.0011, 71.6725),
    "Andijon":   (40.7829, 72.3442),
    "Farg'ona":  (40.3842, 71.7843),
    "Qarshi":    (38.8600, 65.7900),
    "Nukus":     (42.4600, 59.6200),
    "Termiz":    (37.2242, 67.2783),
    "Urganch":   (41.5500, 60.6333),
    "Navoiy":    (40.0840, 65.3792),
    "Jizzax":    (40.1158, 67.8422),
}

API_MAP = {
    "Fajr":    "Bomdod",
    "Sunrise": "Quyosh",
    "Dhuhr":   "Peshin",
    "Asr":     "Asr",
    "Maghrib": "Shom",
    "Isha":    "Xufton",
}
PRAYER_ORDER = ["Bomdod", "Quyosh", "Peshin", "Asr", "Shom", "Xufton"]
TABLE_COLS   = ["Bomdod", "Quyosh", "Peshin", "Asr", "Shom", "Xufton"]

DEFAULT_CONFIG = {
    "city":    "Toshkent",
    "method":  3,
    "school":  1,
    "corrections": {"Bomdod":16,"Quyosh":0,"Peshin":-1,
                    "Asr":-1,"Shom":4,"Xufton":-14},
    "alpha":      77,
    "topmost":    False,
    "sound":      True,   # Ovoz: True=yoqilgan, False=o'chirilgan
    "start_mini": True,   # Dastur ochilganda mini rejimda boshlansin
}

# ─── Ranglar ──────────────────────────────────────────────────────────────────
C = {
    'bg':        '#0b6b6a',
    'hbar':      '#085050',
    'timer_bg':  '#0f5e5d',
    'border':    '#1a9a98',
    'text':      '#ffffff',
    'sub':       '#90ccc8',
    'green':     '#2ecc71',
    'red':       '#e74c3c',
    'orange':    '#f39c12',
    'flash':     '#f0d060',
    'dlg_bg':    '#0e4e4e',
    'panel_bg':  '#0c5555',
    'row_odd':   '#0d6060',
    'row_even':  '#0b5555',
    'row_today': '#1a4a00',
    'row_fri':   '#1a3a5a',
    'hdr_bg':    '#085050',
    'btn_hover': '#1a8a88',
}

UZDAYS_SHORT = ["Du","Se","Ch","Pa","Ju","Sh","Ya"]
UZDAYS       = ["Dushanba","Seshanba","Chorshanba",
                "Payshanba","Juma","Shanba","Yakshanba"]


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG / CACHE
# ══════════════════════════════════════════════════════════════════════════════
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            cfg = json.load(open(CONFIG_FILE, encoding='utf-8'))
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            for p in PRAYER_ORDER:
                if p not in cfg["corrections"]:
                    cfg["corrections"][p] = 0
            return cfg
        except Exception:
            pass
    return {k: (v.copy() if isinstance(v, dict) else v)
            for k, v in DEFAULT_CONFIG.items()}

def save_config(cfg):
    json.dump(cfg, open(CONFIG_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

def load_cache():
    if os.path.exists(CACHE_FILE):
        try: return json.load(open(CACHE_FILE, encoding='utf-8'))
        except Exception: pass
    return {}

def save_cache(date_str, times_dict, city):
    cache = load_cache()
    key   = f"{date_str}_{city}"
    cache[key] = times_dict
    today = datetime.date.today()
    for k in list(cache.keys()):
        try:
            if (today - datetime.date.fromisoformat(k.split('_')[0])).days > 14:
                del cache[k]
        except Exception: pass
    json.dump(cache, open(CACHE_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

def load_month_cache():
    if os.path.exists(MONTH_CACHE):
        try: return json.load(open(MONTH_CACHE, encoding='utf-8'))
        except Exception: pass
    return {}

def save_month_cache(key, data):
    cache = load_month_cache()
    cache[key] = data
    json.dump(cache, open(MONTH_CACHE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)


# ══════════════════════════════════════════════════════════════════════════════
#  API FETCH
# ══════════════════════════════════════════════════════════════════════════════
def apply_correction(t_str, minutes):
    if minutes == 0: return t_str
    h, m  = map(int, t_str[:5].split(':'))
    total = (h*60 + m + minutes) % (24*60)
    return f"{total//60:02d}:{total%60:02d}"

def _base_params(cfg):
    city = cfg.get("city", "Toshkent")
    lat, lon = UZB_CITIES.get(city, UZB_CITIES["Toshkent"])
    return lat, lon, cfg.get("method", 3), cfg.get("school", 1)

def fetch_from_api(cfg, date=None):
    if date is None: date = datetime.date.today()
    lat, lon, method, school = _base_params(cfg)
    ts  = int(datetime.datetime.combine(date, datetime.time(12,0)).timestamp())
    url = (f"https://api.aladhan.com/v1/timings/{ts}?"
           + urllib.parse.urlencode(dict(latitude=lat, longitude=lon,
             method=method, school=school, timezonestring="Asia/Tashkent")))
    req = urllib.request.Request(url, headers={"User-Agent":"NamozVaqtlari/4.0"})
    with urllib.request.urlopen(req, timeout=12) as r:
        data = json.loads(r.read())
    if data.get("code") != 200:
        raise ValueError(f"API xatosi: {data.get('status')}")
    raw  = data["data"]["timings"]
    corr = cfg.get("corrections", {})
    return {uzb: apply_correction(raw.get(api,"00:00")[:5], corr.get(uzb,0))
            for api, uzb in API_MAP.items()}

def fetch_month_from_api(cfg, year, month):
    lat, lon, method, school = _base_params(cfg)
    url = (f"https://api.aladhan.com/v1/calendar/{year}/{month}?"
           + urllib.parse.urlencode(dict(latitude=lat, longitude=lon,
             method=method, school=school, timezonestring="Asia/Tashkent")))
    req = urllib.request.Request(url, headers={"User-Agent":"NamozVaqtlari/4.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())
    if data.get("code") != 200:
        raise ValueError(f"API xatosi: {data.get('status')}")
    corr   = cfg.get("corrections", {})
    result = {}
    for dd in data["data"]:
        g    = dd["date"]["gregorian"]
        date = f"{g['year']}-{g['month']['number']:02d}-{int(g['day']):02d}"
        raw  = dd["timings"]
        result[date] = {uzb: apply_correction(raw.get(api,"00:00")[:5],
                                              corr.get(uzb,0))
                        for api, uzb in API_MAP.items()}
    return result

def fetch_next_30_days(cfg):
    today         = datetime.date.today()
    city          = cfg.get("city","Toshkent")
    months_needed = set()
    for i in range(30):
        d = today + datetime.timedelta(days=i)
        months_needed.add((d.year, d.month))
    cache    = load_month_cache()
    all_data = {}
    for (y, m) in months_needed:
        ckey = f"{y}-{m:02d}_{city}"
        if ckey in cache:
            all_data.update(cache[ckey])
        else:
            fetched = fetch_month_from_api(cfg, y, m)
            save_month_cache(ckey, fetched)
            all_data.update(fetched)
    return [(today + datetime.timedelta(days=i),
             all_data.get((today+datetime.timedelta(days=i)).isoformat(), {}))
            for i in range(30)]


# ══════════════════════════════════════════════════════════════════════════════
#  OVOZ
# ══════════════════════════════════════════════════════════════════════════════
def play_adhan():
    try:
        import pygame, numpy as np
        pygame.mixer.init(44100, -16, 2, 512)
        sr = 44100
        def tone(freq, dur, vol=0.70):
            t   = np.linspace(0, dur, int(sr*dur), False)
            w   = np.sin(2*np.pi*freq*t)
            fl  = int(0.08*len(t))
            env = np.ones(len(t))
            env[:fl]  = np.linspace(0,1,fl)
            env[-fl:] = np.linspace(1,0,fl)
            pcm = (w*env*vol*32767).astype(np.int16)
            return np.ascontiguousarray(np.column_stack([pcm,pcm]))
        seq = [(880,.30),(0,.12),(880,.30),(0,.12),(1100,.50),(0,.15),
               (880,.40),(0,.10),(660,.60),(0,.20),(880,.80),(0,.30),
               (990,.40),(0,.10),(880,.60),(0,.10),(770,1.00)]
        for freq, dur in seq:
            if freq == 0: pygame.time.wait(int(dur*1000))
            else:
                pygame.sndarray.make_sound(tone(freq,dur)).play()
                pygame.time.wait(int(dur*1000)+50)
    except Exception:
        _beep_fallback()

def _beep_fallback():
    try:
        if sys.platform == 'win32':
            import winsound
            for f, d in [(880,400),(0,150),(1100,500),(880,400),(660,600)]:
                if f: winsound.Beep(f,d)
        else:
            for cmd in ["paplay /usr/share/sounds/freedesktop/stereo/message.oga",
                        "aplay /usr/share/sounds/alsa/Front_Center.wav",
                        "beep -f 880 -l 400 -D 100 -r 5"]:
                if os.system(cmd+" 2>/dev/null") == 0: break
            else:
                sys.stdout.write('\a\a\a'); sys.stdout.flush()
    except Exception: pass

def play_warning():
    """20 daqiqa oldin — bitta past 'ting' signal (~50% ovoz)."""
    try:
        import pygame, numpy as np
        pygame.mixer.init(44100, -16, 2, 512)
        sr = 44100; dur = 0.55; vol = 0.35
        t   = np.linspace(0, dur, int(sr*dur), False)
        w   = (np.sin(2*np.pi*880*t)*0.6 + np.sin(2*np.pi*1320*t)*0.4)
        fl  = int(0.05*len(t))
        env = np.ones(len(t))
        env[:fl]  = np.linspace(0,1,fl)
        env[-fl:] = np.linspace(1,0,fl)
        decay = np.exp(-3.5*t/dur)
        pcm = (w*env*decay*vol*32767).astype(np.int16)
        pygame.sndarray.make_sound(
            np.ascontiguousarray(np.column_stack([pcm,pcm]))).play()
        pygame.time.wait(int(dur*1000)+100)
    except Exception:
        try:
            if sys.platform == 'win32':
                import winsound; winsound.Beep(1000, 200)
            else:
                sys.stdout.write('\a'); sys.stdout.flush()
        except Exception: pass


# ══════════════════════════════════════════════════════════════════════════════
#  YORDAMCHI
# ══════════════════════════════════════════════════════════════════════════════
def parse_times(raw_list):
    today = datetime.date.today()
    result = []
    for name, t in raw_list:
        h, m = map(int, t.split(':'))
        result.append((name, datetime.datetime.combine(today, datetime.time(h,m))))
    return result

def get_info(times, now):
    if not times:
        return dict(prayer="—", start=None, end=None, remaining=None, active=False)
    for i in range(len(times)-1):
        name, start = times[i]
        _, end = times[i+1]
        if start <= now < end:
            return dict(prayer=name, start=start, end=end,
                        remaining=end-now, active=True)
    if now < times[0][1]:
        return dict(prayer=times[0][0], start=times[0][1],
                    end=times[1][1], remaining=times[0][1]-now, active=False)
    return dict(prayer=times[-1][0], start=times[-1][1],
                end=None, remaining=None, active=True)

def rounded_rect(cv, x1, y1, x2, y2, r=10, **kw):
    pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
           x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
           x1,y2, x1,y2-r, x1,y1+r, x1,y1]
    return cv.create_polygon(pts, smooth=True, **kw)

def icon_btn(cv, x, y, w, h, text, cmd, font=("Helvetica",8,"bold"),
             fg=None, bg=None, hover=None):
    """Canvas ustida kichik tugma yaratish."""
    fg    = fg    or C['sub']
    bg    = bg    or C['timer_bg']
    hover = hover or C['btn_hover']
    rect = rounded_rect(cv, x, y, x+w, y+h, r=6,
                        fill=bg, outline=C['border'], width=1)
    txt  = cv.create_text(x+w//2, y+h//2, text=text,
                          font=font, fill=fg, anchor='center')
    def _on(e):
        cv.itemconfig(rect, fill=hover)
        cv.itemconfig(txt,  fill=C['text'])
    def _off(e):
        cv.itemconfig(rect, fill=bg)
        cv.itemconfig(txt,  fill=fg)
    for tag in (rect, txt):
        cv.tag_bind(tag, "<Enter>",    _on)
        cv.tag_bind(tag, "<Leave>",    _off)
        cv.tag_bind(tag, "<Button-1>", lambda e: cmd())
    return rect, txt


# ══════════════════════════════════════════════════════════════════════════════
#  OYLIK PANEL
# ══════════════════════════════════════════════════════════════════════════════
PANEL_H   = 340
ANIM_STEP = 22
ANIM_MS   = 12

class MonthPanel(tk.Toplevel):
    def __init__(self, parent_app):
        super().__init__(parent_app.root)
        self.app = parent_app
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(bg=C['panel_bg'])

        rx = self.app.root.winfo_x()
        ry = self.app.root.winfo_y() + self.app.cur_h
        self.target_y = ry - PANEL_H
        self.start_y  = ry
        self.geometry(f"{self.app.W}x{PANEL_H}+{rx}+{self.start_y}")
        self.lift()
        self._build()
        self._animate_open()
        self._fetch()

    def _build(self):
        hdr = tk.Frame(self, bg=C['hdr_bg'], height=32)
        hdr.pack(fill='x'); hdr.pack_propagate(False)
        tk.Label(hdr, text="📅  30 KUNLIK NAMOZ VAQTLARI",
                 font=("Helvetica",9,"bold"),
                 fg=C['sub'], bg=C['hdr_bg']).pack(side='left', padx=10)
        self.lbl_city = tk.Label(hdr, text="",
                 font=("Helvetica",8), fg=C['orange'], bg=C['hdr_bg'])
        self.lbl_city.pack(side='left')
        tk.Button(hdr, text="✖", command=self._close,
                  bg=C['red'], fg='white', font=("Helvetica",9,"bold"),
                  relief='flat', padx=8, cursor='hand2').pack(
                  side='right', padx=4, pady=4)

        self.lbl_loading = tk.Label(self, text="⟳  Yuklanmoqda…",
                 font=("Helvetica",10), fg=C['orange'], bg=C['panel_bg'])
        self.lbl_loading.pack(pady=10)

        self.tree_frame = tk.Frame(self, bg=C['panel_bg'])
        self._build_table()

    def _build_table(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Month.Treeview",
            background=C['row_even'], foreground=C['text'],
            fieldbackground=C['row_even'], rowheight=22,
            font=("Helvetica",8), borderwidth=0)
        style.configure("Month.Treeview.Heading",
            background=C['hdr_bg'], foreground=C['sub'],
            font=("Helvetica",8,"bold"), relief='flat')
        style.map("Month.Treeview",
            background=[('selected','#1a7a6a')],
            foreground=[('selected','white')])
        style.layout("Month.Treeview",
            [('Month.Treeview.treearea',{'sticky':'nswe'})])

        cols = ("sana","kun") + tuple(TABLE_COLS)
        self.tree = ttk.Treeview(self.tree_frame, columns=cols,
                                  show='headings', style="Month.Treeview",
                                  selectmode='none', height=13)
        self.tree.column("sana", width=46,  anchor="center", stretch=False)
        self.tree.column("kun",  width=24,  anchor="center", stretch=False)
        for p in TABLE_COLS:
            self.tree.column(p, width=52, anchor="center", stretch=False)
        self.tree.heading("sana", text="Sana")
        self.tree.heading("kun",  text="Kun")
        for p in TABLE_COLS: self.tree.heading(p, text=p)

        sb = ttk.Scrollbar(self.tree_frame, orient='vertical',
                           command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        self.tree.tag_configure('today',
            background=C['row_today'], foreground='#aaffaa')
        self.tree.tag_configure('friday',
            background=C['row_fri'],   foreground='#aaccff')
        self.tree.tag_configure('odd',  background=C['row_odd'])
        self.tree.tag_configure('even', background=C['row_even'])

    def _fetch(self):
        city = self.app.cfg.get("city","Toshkent")
        self.lbl_city.config(text=f"— {city}")
        def _do():
            try:
                rows = fetch_next_30_days(self.app.cfg)
                self.app.root.after(0, lambda: self._populate(rows))
            except Exception as e:
                self.app.root.after(0, lambda:
                    self.lbl_loading.config(
                        text=f"❌  Xatolik: {e}", fg=C['red']))
        threading.Thread(target=_do, daemon=True).start()

    def _populate(self, rows):
        self.lbl_loading.pack_forget()
        self.tree_frame.pack(fill='both', expand=True, padx=4, pady=(0,4))
        today     = datetime.date.today()
        today_iid = None
        for i, (d, times) in enumerate(rows):
            is_today  = (d == today)
            is_friday = (d.weekday() == 4)
            tag = 'today' if is_today else (
                  'friday' if is_friday else (
                  'odd' if i%2==0 else 'even'))
            vals = (d.strftime("%d.%m"), UZDAYS_SHORT[d.weekday()]) + \
                   tuple(times.get(p,"--:--") for p in TABLE_COLS)
            iid = self.tree.insert('', 'end', values=vals, tags=(tag,))
            if is_today: today_iid = iid
        if today_iid: self.tree.see(today_iid)

    def _animate_open(self, cur_y=None):
        if cur_y is None: cur_y = self.start_y
        rx  = self.app.root.winfo_x()
        new_y = max(self.target_y, cur_y - ANIM_STEP)
        self.geometry(f"{self.app.W}x{PANEL_H}+{rx}+{new_y}")
        if new_y > self.target_y:
            self.after(ANIM_MS, lambda: self._animate_open(new_y))

    def _animate_close(self, cur_y=None):
        if cur_y is None: cur_y = self.target_y
        rx  = self.app.root.winfo_x()
        new_y = min(self.start_y, cur_y + ANIM_STEP)
        self.geometry(f"{self.app.W}x{PANEL_H}+{rx}+{new_y}")
        if new_y < self.start_y:
            self.after(ANIM_MS, lambda: self._animate_close(new_y))
        else:
            self.destroy()
            self.app.panel = None

    def _close(self): self._animate_close()


# ══════════════════════════════════════════════════════════════════════════════
#  SOZLAMALAR OYNASI
# ══════════════════════════════════════════════════════════════════════════════
class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, cfg, on_save):
        super().__init__(parent)
        self.cfg, self.on_save = cfg, on_save
        self.overrideredirect(True)       # oq titlebar o'rniga dark header
        self.geometry("380x610")
        self.resizable(False, False)
        self.configure(bg=C['dlg_bg'])
        self.grab_set()
        self._dx = self._dy = 0
        self._build()
        # Markazlash
        self.update_idletasks()
        pw = parent.winfo_x(); ph = parent.winfo_y()
        x  = pw + (parent.winfo_width()  - 380) // 2
        y  = ph + (parent.winfo_height() - 610) // 2
        self.geometry(f"380x610+{x}+{y}")

    # ── Drag ────────────────────────────────────────────────────────────────
    def _start_drag(self, e): self._dx = e.x_root; self._dy = e.y_root
    def _do_drag(self, e):
        self.geometry(f"+{self.winfo_x()+(e.x_root-self._dx)}"
                      f"+{self.winfo_y()+(e.y_root-self._dy)}")
        self._dx = e.x_root; self._dy = e.y_root

    def _label(self, parent, text, small=False):
        tk.Label(parent, text=text,
                 font=("Helvetica", 7 if small else 9),
                 fg=C['sub'], bg=C['dlg_bg'],
                 anchor='w').pack(fill='x', padx=12, pady=(4,1))

    def _sep(self, parent):
        tk.Frame(parent, height=1, bg=C['border']).pack(
            fill='x', padx=10, pady=5)

    def _build(self):
        bg = C['dlg_bg']

        # ── Dark titlebar (drag handle) ──────────────────────────────────────
        tbar = tk.Frame(self, bg=C['hbar'], height=36)
        tbar.pack(fill='x'); tbar.pack_propagate(False)
        tk.Label(tbar, text="  SOZLAMALAR",
                 font=("Helvetica",11,"bold"),
                 fg=C['text'], bg=C['hbar']).pack(side='left', padx=6)
        tk.Button(tbar, text="X", command=self.destroy,
                  bg=C['red'], fg='white',
                  font=("Helvetica",9,"bold"),
                  relief='flat', bd=0, padx=8,
                  cursor='hand2').pack(side='right', padx=4, pady=4)
        tbar.bind("<ButtonPress-1>",   self._start_drag)
        tbar.bind("<B1-Motion>",       self._do_drag)

        self._sep(self)

        # ── Shahar ───────────────────────────────────────────────────────────
        self._label(self, "Shahar:")
        self.city_var = tk.StringVar(value=self.cfg.get("city","Toshkent"))
        ttk.Combobox(self, textvariable=self.city_var,
                     values=sorted(UZB_CITIES.keys()),
                     state='readonly', font=("Helvetica",10),
                     width=22).pack(padx=12, pady=2, anchor='w')

        # ── Hisoblash usuli ──────────────────────────────────────────────────
        self._label(self, "Hisoblash usuli:  (ISLOM.uz = Method 3 + Hanafi)")
        self._methods = {
            "3 — Muslim World League  [ISLOM.uz]": 3,
            "1 — Karachi universiteti":            1,
            "2 — ISNA (Shimoliy Amerika)":         2,
            "4 — Umm al-Qura (Makka)":             4,
        }
        self.method_var = tk.StringVar()
        cur_m = self.cfg.get("method", 3)
        for lbl, val in self._methods.items():
            if val == cur_m: self.method_var.set(lbl); break
        ttk.Combobox(self, textvariable=self.method_var,
                     values=list(self._methods.keys()),
                     state='readonly', font=("Helvetica",8),
                     width=36).pack(padx=12, pady=2, anchor='w')

        self._sep(self)

        # ── UMI Tuzatish ─────────────────────────────────────────────────────
        tk.Label(self,
                 text="UMI tuzatish  (+-daqiqa  |  ISLOM.uz bilan solishtirib):",
                 font=("Helvetica",8,"bold"),
                 fg=C['orange'], bg=bg).pack(fill='x', padx=12, pady=(0,2))
        self.corr_vars = {}
        corr = self.cfg.get("corrections", {})
        fr   = tk.Frame(self, bg=bg)
        fr.pack(fill='x', padx=12, pady=2)
        for i, name in enumerate(PRAYER_ORDER):
            r, c = divmod(i, 3)
            tk.Label(fr, text=name, font=("Helvetica",8),
                     fg=C['sub'], bg=bg, width=8,
                     anchor='w').grid(row=r*2, column=c,
                                      sticky='w', padx=4, pady=1)
            var = tk.IntVar(value=corr.get(name, 0))
            self.corr_vars[name] = var
            tk.Spinbox(fr, from_=-30, to=30, textvariable=var,
                       width=5, font=("Helvetica",9),
                       bg='#1a8080', fg='white',
                       buttonbackground='#1a8080',
                       relief='flat',
                       highlightthickness=0).grid(
                       row=r*2+1, column=c,
                       sticky='w', padx=4, pady=2)

        self._sep(self)

        # ── KO'RINISH ────────────────────────────────────────────────────────
        tk.Label(self, text="  KO'RINISH",
                 font=("Helvetica",9,"bold"),
                 fg=C['text'], bg=bg).pack(fill='x', padx=12)

        # Shaffoflik
        self._label(self, "Shaffoflik (Transparency):")
        alpha_fr = tk.Frame(self, bg=bg)
        alpha_fr.pack(fill='x', padx=12, pady=2)
        self.alpha_var = tk.IntVar(value=self.cfg.get("alpha", 77))
        self.alpha_lbl = tk.Label(alpha_fr,
                 text=f"{self.alpha_var.get()}%",
                 font=("Helvetica",9,"bold"),
                 fg=C['orange'], bg=bg, width=5)
        self.alpha_lbl.pack(side='right')
        tk.Label(alpha_fr, text="30%", font=("Helvetica",7),
                 fg=C['sub'], bg=bg).pack(side='left')
        ttk.Scale(alpha_fr, from_=30, to=100,
                  variable=self.alpha_var,
                  orient='horizontal', length=200).pack(side='left', padx=4)
        tk.Label(alpha_fr, text="100%", font=("Helvetica",7),
                 fg=C['sub'], bg=bg).pack(side='left')
        self.alpha_var.trace_add('write',
            lambda *a: self.alpha_lbl.config(
                text=f"{self.alpha_var.get()}%"))

        # Har doim ustda
        self._label(self, "Oyna pozitsiyasi:")
        top_fr = tk.Frame(self, bg=bg)
        top_fr.pack(fill='x', padx=12, pady=2)
        self.topmost_var = tk.BooleanVar(value=self.cfg.get("topmost", False))
        tk.Checkbutton(top_fr,
                 text="Har doim boshqa oynalardan USTDA bo'lsin",
                 variable=self.topmost_var,
                 font=("Helvetica",9),
                 fg=C['text'], bg=bg,
                 selectcolor=C['timer_bg'],
                 activebackground=bg,
                 activeforeground=C['text']).pack(anchor='w')

        # Ovoz
        self._label(self, "Ovoz sozlamalari:")
        snd_fr = tk.Frame(self, bg=bg)
        snd_fr.pack(fill='x', padx=12, pady=2)
        self.sound_var = tk.BooleanVar(value=self.cfg.get("sound", True))
        tk.Checkbutton(snd_fr,
                 text="Namoz vaqtida ovozli signal (adhan)",
                 variable=self.sound_var,
                 font=("Helvetica",9),
                 fg=C['text'], bg=bg,
                 selectcolor=C['timer_bg'],
                 activebackground=bg,
                 activeforeground=C['text']).pack(anchor='w')

        # Mini rejimda boshlansin
        self._label(self, "Ishga tushganda:")
        mini_fr = tk.Frame(self, bg=bg)
        mini_fr.pack(fill='x', padx=12, pady=2)
        self.start_mini_var = tk.BooleanVar(
            value=self.cfg.get("start_mini", True))
        tk.Checkbutton(mini_fr,
                 text="Mini rejimda boshlansin",
                 variable=self.start_mini_var,
                 font=("Helvetica",9),
                 fg=C['text'], bg=bg,
                 selectcolor=C['timer_bg'],
                 activebackground=bg,
                 activeforeground=C['text']).pack(anchor='w')

        self._sep(self)

        # ── Tugmalar ─────────────────────────────────────────────────────────
        bf = tk.Frame(self, bg=bg); bf.pack(pady=4)
        tk.Button(bf, text="  Saqlash", command=self._save,
                  bg=C['green'], fg='white',
                  font=("Helvetica",10,"bold"),
                  relief='flat', padx=16, pady=6,
                  cursor='hand2').pack(side='left', padx=8)
        tk.Button(bf, text="  Bekor", command=self.destroy,
                  bg=C['red'], fg='white',
                  font=("Helvetica",10,"bold"),
                  relief='flat', padx=16, pady=6,
                  cursor='hand2').pack(side='left', padx=8)

    def _save(self):
        self.cfg["city"]        = self.city_var.get()
        self.cfg["method"]      = self._methods.get(self.method_var.get(), 3)
        self.cfg["corrections"] = {n: v.get() for n,v in self.corr_vars.items()}
        self.cfg["alpha"]       = int(self.alpha_var.get())
        self.cfg["topmost"]     = self.topmost_var.get()
        self.cfg["sound"]       = self.sound_var.get()
        self.cfg["start_mini"]  = self.start_mini_var.get()
        save_config(self.cfg)
        self.on_save()
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
#  ASOSIY ILOVA
# ══════════════════════════════════════════════════════════════════════════════
class PrayerApp:
    W       = 400
    H_FULL  = 236    # To'liq rejim
    H_MINI  = 46     # Mini rejim

    def __init__(self, root):
        self.root = root
        self.root.title("Namoz Vaqtlari")
        self.root.resizable(False, False)
        self.root.configure(bg=C['bg'])

        self.cfg        = load_config()
        self.alerted    = set()
        self.times_raw  = []
        self._last_date = None
        self.panel      = None
        self.mini       = False
        self.cur_h      = self.H_FULL
        self._drag_x    = 0
        self._drag_y    = 0

        # Taskbardan yashirish + shaffoflik
        self.root.overrideredirect(True)
        self._apply_window_cfg()
        self.root.geometry(f"{self.W}x{self.H_FULL}+40+40")

        self._build()

        # Drag (header orqali ko'chirish)
        self.cv.bind("<ButtonPress-1>",  self._drag_start)
        self.cv.bind("<B1-Motion>",      self._drag_move)

        self.cv.bind("<Button-3>",   self._context_menu)
        self.root.bind("<Button-3>", self._context_menu)

        self._load_times_async()
        self._tick()

        # Boshlanganda mini rejim
        if self.cfg.get("start_mini", True):
            self.root.after(100, self._toggle_mini)

    def _drag_start(self, e):
        if e.y <= self.H_MINI:   # faqat header zonasida
            self._drag_x = e.x_root
            self._drag_y = e.y_root

    def _drag_move(self, e):
        if e.y <= self.H_MINI or self.mini:
            dx = e.x_root - self._drag_x
            dy = e.y_root - self._drag_y
            nx = self.root.winfo_x() + dx
            ny = self.root.winfo_y() + dy
            self.root.geometry(f"+{nx}+{ny}")
            self._drag_x = e.x_root
            self._drag_y = e.y_root

    def _apply_window_cfg(self):
        alpha   = self.cfg.get("alpha",   77) / 100.0
        topmost = self.cfg.get("topmost", False)
        self.root.attributes('-alpha',   alpha)
        self.root.attributes('-topmost', topmost)

    # ── Fetch ────────────────────────────────────────────────────────────────
    def _load_times_async(self, force=False):
        self._set_status("⟳", C['orange'])
        def _do():
            today = datetime.date.today()
            city  = self.cfg.get("city","Toshkent")
            key   = f"{today.isoformat()}_{city}"
            cache = load_cache()
            if not force and key in cache:
                raw = [(p, cache[key][p]) for p in PRAYER_ORDER
                       if p in cache[key]]
                src = "cache"
            else:
                try:
                    d   = fetch_from_api(self.cfg)
                    save_cache(today.isoformat(), d, city)
                    raw = [(p, d[p]) for p in PRAYER_ORDER]
                    src = "api"
                except Exception as e:
                    print(f"[API] {e}"); raw = []; src = "offline"
            self.times_raw  = raw
            self._last_date = today
            self.root.after(0, lambda: self._on_loaded(src, city))
        threading.Thread(target=_do, daemon=True).start()

    def _on_loaded(self, src, city):
        icons = {"api":"🟢","cache":"💾","offline":"🔴"}
        color = {"api":C['green'],"cache":C['sub'],"offline":C['red']}
        self._set_status(f"{icons[src]} {city}", color[src])

    # ── UI build ─────────────────────────────────────────────────────────────
    def _build(self):
        W = self.W
        bg = C['bg']
        # Canvas to'liq balandlikda — mini rejimda pastki qism yashiriladi
        self.cv = Canvas(self.root, width=W, height=self.H_FULL,
                         bg=bg, bd=0, highlightthickness=0)
        self.cv.pack()

        # ── Header (har doim ko'rinadigan, H_MINI) ──────────────────────────
        # Ustki rang chizig'i
        self.cv.create_rectangle(0, 0, W, 3, fill=C['border'], outline='')
        # Header fon
        self.cv.create_rectangle(0, 3, W, self.H_MINI,
                                 fill=C['hbar'], outline='')

        # ⚙ Sozlamalar tugmasi (chap)
        icon_btn(self.cv, 6, 8, 28, 30, "⚙",
                 self._open_settings,
                 font=("Helvetica",10), fg=C['sub'])

        # 📅 Jadval tugmasi (chapdan 2-chi)
        icon_btn(self.cv, 40, 8, 28, 30, "📅",
                 self._toggle_panel,
                 font=("Helvetica",10), fg=C['sub'])

        # 🗕 Mini/Max tugmasi — eng o'ngda, header ichida
        self._mini_btn_r, self._mini_btn_t = icon_btn(
                 self.cv, W-36, 8, 28, 30, "▼",
                 self._toggle_mini,
                 font=("Helvetica",10,"bold"), fg=C['sub'])

        # Mini rejimda markazda: "Peshin — 02:14:33"
        self.id_mini_prayer = self.cv.create_text(
            W//2, 25, text="",
            font=("Helvetica",13,"bold"),
            fill=C['text'], anchor='center', state='hidden')

        # ── Full mode: qolgan qism ──────────────────────────────────────────
        self._full_ids = []   # mini rejimda yashiriladigan elementlar

        def fc(*args, **kw):
            method = args[0]
            iid    = getattr(self.cv, method)(*args[1:], **kw)
            self._full_ids.append(iid)
            return iid

        # Hozirgi soat — full modeda header ostida, o'ngda
        self.id_clock = fc('create_text',
            W-6, self.H_MINI+13, text="--:--:--",
            font=("Helvetica",10,"bold"),
            fill=C['text'], anchor='e')

        # JORIY NAMOZ sarlavha — full modeda soat yonida chap tomonda
        self.id_title = fc('create_text',
            W//2, self.H_MINI+13, text="JORIY NAMOZ",
            font=("Helvetica",8,"bold"), fill=C['sub'], anchor='center')

        # Namoz nomi (katta)
        self.id_name = fc('create_text',
            W//2, self.H_MINI+46, text="⟳",
            font=("Helvetica",26,"bold"), fill=C['text'], anchor='center')

        # Qolgan vaqt sarlavha
        self.id_rem_lbl = fc('create_text',
            W//2, self.H_MINI+72, text="QOLGAN VAQT",
            font=("Helvetica",7), fill=C['sub'], anchor='center')

        # Timer box
        TY1 = self.H_MINI+79; TY2 = self.H_MINI+115
        rounded_rect(self.cv, 100, TY1, 300, TY2, r=14,
                     fill=C['timer_bg'], outline=C['border'], width=1)
        self._full_ids.append(self.cv.find_all()[-1])  # polygon
        self.id_timer = fc('create_text',
            W//2, self.H_MINI+97, text="--:--:--",
            font=("Helvetica",21,"bold"), fill=C['text'], anchor='center')

        # BOSHLANDI doira
        CY = self.H_MINI + 150
        self.cv.create_oval(32, CY-28, 88, CY+28,
                            outline=C['green'], fill='', width=2)
        self._full_ids.append(self.cv.find_all()[-1])
        self._full_ids.append(self.cv.create_text(
            60, CY-18, text="BOSHLANDI",
            font=("Helvetica",6,"bold"), fill=C['green'], anchor='center'))
        self.id_starts = fc('create_text',
            60, CY+2, text="--:--",
            font=("Helvetica",13,"bold"), fill=C['text'], anchor='center')

        # TUGAYDI doira
        self.cv.create_oval(312, CY-28, 368, CY+28,
                            outline=C['red'], fill='', width=2)
        self._full_ids.append(self.cv.find_all()[-1])
        self._full_ids.append(self.cv.create_text(
            340, CY-18, text="TUGAYDI",
            font=("Helvetica",6,"bold"), fill=C['red'], anchor='center'))
        self.id_ends = fc('create_text',
            340, CY+2, text="--:--",
            font=("Helvetica",13,"bold"), fill=C['text'], anchor='center')

        # Keyingi namoz
        self.id_next_lbl = fc('create_text',
            W//2, CY-8, text="",
            font=("Helvetica",7), fill=C['sub'], anchor='center')
        self.id_next = fc('create_text',
            W//2, CY+10, text="",
            font=("Helvetica",11,"bold"), fill=C['orange'], anchor='center')

        # Sana + Status
        self.id_date = fc('create_text',
            4, self.H_FULL-8, text="",
            font=("Helvetica",7), fill=C['sub'], anchor='sw')
        self.id_status = fc('create_text',
            W-4, self.H_FULL-8, text="",
            font=("Helvetica",7), fill=C['orange'], anchor='se')

    def _set_status(self, text, color):
        self.cv.itemconfig(self.id_status, text=text, fill=color)

    # ── Mini rejim ──────────────────────────────────────────────────────────
    def _toggle_mini(self):
        x, y = self.root.winfo_x(), self.root.winfo_y()
        if self.mini:
            # Kengaytir
            self.mini   = False
            self.cur_h  = self.H_FULL
            self.root.geometry(f"{self.W}x{self.H_FULL}+{x}+{y}")
            for iid in self._full_ids:
                self.cv.itemconfig(iid, state='normal')
            self.cv.itemconfig(self.id_mini_prayer, state='hidden')
            self.cv.itemconfig(self._mini_btn_t, text="▼")
        else:
            # Mini rejim
            self.mini   = True
            self.cur_h  = self.H_MINI
            self.root.geometry(f"{self.W}x{self.H_MINI}+{x}+{y}")
            for iid in self._full_ids:
                self.cv.itemconfig(iid, state='hidden')
            self.cv.itemconfig(self.id_mini_prayer, state='normal')
            self.cv.itemconfig(self._mini_btn_t, text="▲")
        # Panelni yopish
        if self.panel and self.panel.winfo_exists():
            self.panel.destroy()
            self.panel = None

    # ── Oylik panel ─────────────────────────────────────────────────────────
    def _toggle_panel(self):
        if self.panel and self.panel.winfo_exists():
            self.panel._close()
        else:
            if not self.mini:
                self.panel = MonthPanel(self)

    # ── Tick ────────────────────────────────────────────────────────────────
    def _tick(self):
        now   = datetime.datetime.now()
        today = datetime.date.today()

        if self._last_date and self._last_date != today:
            self._load_times_async(force=True)

        # Hozirgi soatni yangilash (har doim)
        self.cv.itemconfig(self.id_clock,
            text=now.strftime("%H:%M:%S"))

        times = parse_times(self.times_raw)
        info  = get_info(times, now)

        prayer = info['prayer']
        start  = info['start']
        end    = info['end']
        rem    = info['remaining']
        active = info['active']

        # Timer string
        if rem is not None:
            tot = max(0, int(rem.total_seconds()))
            h, m, s = tot//3600, (tot%3600)//60, tot%60
            timer_str  = f"{h:02d}:{m:02d}:{s:02d}"
            timer_col  = C['orange'] if tot < 1200 else C['text']
        else:
            timer_str = "✓  Barakalla"
            timer_col = C['green']

        # Mini rejim: markazda "Peshin — 02:14:33"
        if self.mini:
            if rem is not None:
                self.cv.itemconfig(self.id_mini_prayer,
                    text=f"{prayer}  —  {timer_str}",
                    fill=timer_col)
            else:
                self.cv.itemconfig(self.id_mini_prayer,
                    text=f"✓ {prayer}", fill=C['green'])
        else:
            # Full rejim
            self.cv.itemconfig(self.id_name, text=prayer)
            if active:
                self.cv.itemconfig(self.id_title,   text="JORIY NAMOZ")
                self.cv.itemconfig(self.id_rem_lbl, text="TUGASHIGA QOLDI")
            else:
                self.cv.itemconfig(self.id_title,   text="KEYINGI NAMOZ")
                self.cv.itemconfig(self.id_rem_lbl, text="BOSHLANISHIGA QOLDI")

            self.cv.itemconfig(self.id_timer,
                text=timer_str, fill=timer_col)
            self.cv.itemconfig(self.id_starts,
                text=start.strftime("%H:%M") if start else "--:--")
            self.cv.itemconfig(self.id_ends,
                text=end.strftime("%H:%M")   if end   else "--:--")

            if active and end:
                nxt = next((n for n,dt in times if dt==end), None)
                if nxt:
                    self.cv.itemconfig(self.id_next_lbl, text="KEYINGI")
                    self.cv.itemconfig(self.id_next,
                        text=f"{nxt}  {end.strftime('%H:%M')}")
                else:
                    self.cv.itemconfig(self.id_next_lbl, text="")
                    self.cv.itemconfig(self.id_next, text="")
            else:
                self.cv.itemconfig(self.id_next_lbl, text="")
                self.cv.itemconfig(self.id_next, text="")

            day = UZDAYS[now.weekday()]
            self.cv.itemconfig(self.id_date,
                text=f"{day}  {now.strftime('%d.%m.%Y')}")

        # Panel pozitsiyasi
        if self.panel and self.panel.winfo_exists():
            rx = self.root.winfo_x()
            ry = self.root.winfo_y() + self.cur_h
            self.panel.target_y = ry - PANEL_H
            self.panel.geometry(
                f"{self.W}x{PANEL_H}+{rx}+{self.panel.target_y}")

        self._check_alert(times, now)
        self.root.after(1000, self._tick)

    # ── Alert ────────────────────────────────────────────────────────────────
    def _check_alert(self, times, now):
        sound_on = self.cfg.get("sound", True)
        for name, dt in times:
            ds   = str(dt.date())
            diff = (now - dt).total_seconds()

            key_in = f"{name}_{ds}_in"
            if 0 <= diff < 60 and key_in not in self.alerted:
                self.alerted.add(key_in)
                if sound_on:
                    threading.Thread(target=play_adhan, daemon=True).start()
                self._flash()

            warn_dt   = dt - datetime.timedelta(minutes=20)
            warn_diff = (now - warn_dt).total_seconds()
            key_warn  = f"{name}_{ds}_warn"
            if 0 <= warn_diff < 60 and key_warn not in self.alerted:
                self.alerted.add(key_warn)
                if sound_on:
                    threading.Thread(target=play_warning, daemon=True).start()

    def _flash(self, n=0):
        bg = C['flash'] if n % 2 == 0 else C['bg']
        self.cv.configure(bg=bg); self.root.configure(bg=bg)
        if n < 2:
            self.root.after(350, lambda: self._flash(n+1))
        else:
            self.cv.configure(bg=C['bg']); self.root.configure(bg=C['bg'])

    # ── Context menyu ────────────────────────────────────────────────────────
    def _context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0,
                       bg=C['dlg_bg'], fg=C['text'],
                       activebackground=C['border'],
                       font=("Helvetica",9))
        menu.add_command(label="⚙  Sozlamalar",  command=self._open_settings)
        menu.add_command(label="🔄  Qayta yuklash",
                         command=lambda: self._load_times_async(force=True))
        menu.add_separator()
        mini_lbl = "▲  Kengaytirish" if self.mini else "▼  Mini rejim"
        menu.add_command(label=mini_lbl, command=self._toggle_mini)
        menu.add_separator()
        menu.add_command(label="✖  Yopish", command=self.root.destroy)
        menu.tk_popup(event.x_root, event.y_root)

    def _open_settings(self):
        def on_save():
            self.cfg = load_config()
            self._apply_window_cfg()
            if os.path.exists(MONTH_CACHE): os.remove(MONTH_CACHE)
            self._load_times_async(force=True)
        SettingsDialog(self.root, self.cfg, on_save)


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    PrayerApp(root)
    root.mainloop()
