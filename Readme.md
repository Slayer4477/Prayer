               # Namoz Vaqtlari — To'liq Qo'llanma

---

## Tezkor boshlash

> **install.bat** faylini **2 marta bosing** — hammasi o'zi bo'ladi.

Shundan keyin dastur ishga tushadi va kompyuter har yoqilganda avtomatik ochiladi.

---

## Mundarija

1. [Nima bu dastur?](#1-nima-bu-dastur)
2. [Talablar](#2-talablar)
3. [Fayllar nima?](#3-fayllar-nima)
4. [O'rnatish](#4-ornatish)
5. [Dastur oynasi](#5-dastur-oynasi)
6. [Mini rejim](#6-mini-rejim)
7. [30 kunlik jadval](#7-30-kunlik-jadval)
8. [Sozlamalar](#8-sozlamalar)
9. [Ovoz signallari](#9-ovoz-signallari)
10. [Namoz vaqtlari qanday hisoblanadi?](#10-namoz-vaqtlari-qanday-hisoblanadi)
11. [Taskbardan yashirilgan — qanday topaman?](#11-taskbardan-yashirilgan--qanday-topaman)
12. [O'chirish](#12-ochirish)
13. [Muammolar va yechimlar](#13-muammolar-va-yechimlar)

---

## 1. Nima bu dastur?

**Namoz Vaqtlari** — O'zbekiston uchun mo'ljallangan, ekranda doim ko'rinib turuvchi namoz vaqtlari eslatmasi.

**Asosiy xususiyatlar:**

- Bugungi namoz vaqtlarini internetdan avtomatik yuklaydi
- Keyingi namozga qancha vaqt qolganini sanab turadi
- Namoz vaqti kirganda **ovozli signal** beradi
- 20 daqiqa oldin **ogohlantirib qo'yadi**
- 30 kunlik jadvalni bir bosish bilan ko'rsatadi
- Kompyuter yoqilganda avtomatik ochiladi
- Taskbarda ko'rinmaydi — ekranda kichkina widget sifatida turadi

---

## 2. Talablar

| | Talab |
|---|---|
| Operatsion tizim | Windows 10 / 11 |
| Python | 3.8 yoki undan yuqori |
| Internet | Birinchi ishga tushganda (keyin offline ishlaydi) |

**Python o'rnatilmagan bo'lsa:** [python.org](https://python.org) ga kiring, yuklab o'rnating.
O'rnatishda **"Add Python to PATH"** katagiga belgi qo'yishni unutmang.

---

## 3. Fayllar nima?

```
Prayer/
  namoz_vaqtlari.py   — Dasturning asosiy kodi
  namoz.ico           — Dastur ikonkasi
  build.bat           — EXE fayl yaratuvchi skript
  install.bat         — O'rnatuvchi skript (shu ni bosing)
  README.md           — Shu qo'llanma
```

`install.bat` ishlagandan keyin quyidagilar yaratiladi:

```
D:\Prayer\
  NamozVaqtlari.exe   — Asosiy dastur (Python shart emas)
  namoz.ico           — Ikonka
  config.json         — Sozlamalar (avtomatik yaratiladi)
  times_cache.json    — Yuklab olingan vaqtlar (cache)
  month_cache.json    — 30 kunlik jadval cache
```

---

## 4. O'rnatish

### Qadam 1 — Python o'rnatish (agar yo'q bo'lsa)

1. [python.org/downloads](https://python.org/downloads) ga kiring
2. Eng yangi versiyani yuklab o'rnating
3. O'rnatishda **"Add Python to PATH"** katagiga albatta belgi qo'ying

### Qadam 2 — EXE yaratish

1. `build.bat` faylini **2 marta bosing**
2. Konsol oynasi ochiladi — **hech narsa qilmang, kuting** (1–3 daqiqa)
3. Tugagach `dist\` papkasi avtomatik ochiladi

### Qadam 3 — O'rnatish

1. `install.bat` faylini **2 marta bosing**
2. O'zi quyidagilarni bajaradi:
   - `D:\Prayer\` papkasini yaratadi
   - Barcha fayllarni u yerga ko'chiradi
   - Autostart ga qo'shadi
   - Dasturni darhol ishga tushiradi

Hammasi shu — boshqa hech narsa kerak emas.

---

## 5. Dastur oynasi

Dastur **400×236** piksel o'lchamidagi kichkina oyna ko'rinishida ishlaydi.

```
┌─────────────────────────────────────────┐
│ ⚙  📅         Peshin        14:35:22 ▼ │  ← Header
├─────────────────────────────────────────┤
│              JORIY NAMOZ                │
│                Peshin                   │  ← Namoz nomi
│            TUGASHIGA QOLDI              │
│          ┌──────────────────┐           │
│          │   02:14:33       │           │  ← Qolgan vaqt
│          └──────────────────┘           │
│  🟢 BOSHLANDI  KEYINGI  TUGAYDI 🔴     │
│     12:21     Asr 17:08    17:08        │
│                                         │
│ Dushanba 20.04.2026          🟢 Toshk. │
└─────────────────────────────────────────┘
```

**Elementlar:**

| Element | Tavsif |
|---|---|
| **Joriy namoz nomi** | Hozir qaysi namoz vaqtida ekanligimiz |
| **Qolgan vaqt** | Namoz tugashiga qancha qoldi (HH:MM:SS) |
| **BOSHLANDI** | Joriy namoz boshlanish vaqti |
| **TUGAYDI** | Joriy namoz tugash vaqti |
| **KEYINGI** | Keyingi namoz nomi va vaqti |
| **Soat** (o'ng yuqori) | Hozirgi vaqt, har soniya yangilanadi |
| **Status** (o'ng quyi) | 🟢 Internet / 💾 Cache / 🔴 Offline |

**Oynani ko'chirish:** Header qismini sichqoncha bilan ushlab sudrang.

**Timer ranglari:**
- Oq — odatdagi holat
- Sariq — 20 daqiqadan kam qoldi
- Yashil + "Barakalla" — namoz vaqti kirgandan keyin

---

## 6. Mini rejim

Header dagi **▼** tugmasini bosing — oyna kichrayib qoladi:

```
┌──────────────────────────────────────────┐
│ ⚙  📅    Peshin — 02:14:33   14:35  ▲  │
└──────────────────────────────────────────┘
```

- Faqat namoz nomi + qolgan vaqt ko'rinadi
- Juda kam joy egallaydi
- Qaytish uchun **▲** tugmasini bosing

**Eslatma:** Dastur default holda mini rejimda boshlanadi.

---

## 7. 30 kunlik jadval

Header dagi **📅** tugmasini bosing — pastdan jadval siljib chiqadi:

| Sana | Kun | Bomdod | Quyosh | Peshin | Asr | Shom | Xufton |
|---|---|---|---|---|---|---|---|
| 20.04 | Du | 04:11 | 05:36 | 12:21 | 17:08 | 19:12 | 20:29 |
| 21.04 | Se | 04:09 | 05:34 | 12:21 | 17:09 | 19:13 | 20:31 |
| ... | | | | | | | |

**Ranglar:**
- 🟩 Yashil — bugungi kun
- 🔵 Ko'k — Juma kunlari

Yopish uchun jadval yuqorisidagi **✖** tugmasini bosing.

**Cache:** Jadval bir marta yuklanib saqlanadi. Internet kerak bo'lmaydi qayta ko'rishda.

---

## 8. Sozlamalar

Header dagi **⚙** tugmasini yoki **o'ng klik → Sozlamalar** orqali oching.

### Shahar

O'zbekistonning 12 ta shahri mavjud:

> Toshkent, Samarqand, Buxoro, Namangan, Andijon, Farg'ona,
> Qarshi, Nukus, Termiz, Urganch, Navoiy, Jizzax

### Hisoblash usuli

| Usul | Tavsif |
|---|---|
| **Method 3 — Muslim World League** | ISLOM.uz bilan mos ✓ (tavsiya) |
| Method 1 — Karachi | Janubiy Osiyo |
| Method 2 — ISNA | Shimoliy Amerika |
| Method 4 — Umm al-Qura | Makka |

### UMI Tuzatish

API vaqtlari ISLOM.uz jadvali bilan bir-ikki daqiqa farq qilishi mumkin.
Har bir namoz uchun **±30 daqiqa** oralig'ida tuzatish kiriting.

**Misol:** Agar API Bomdodni `04:08` desa, ISLOM.uz `04:11` desa → `+3` kiriting.

Toshkent uchun tavsiya etilgan tuzatishlar (default):

| Namoz | Tuzatish |
|---|---|
| Bomdod | +16 |
| Quyosh | 0 |
| Peshin | -1 |
| Asr | -1 |
| Shom | +4 |
| Xufton | -14 |

### Ko'rinish sozlamalari

| Sozlama | Tavsif | Default |
|---|---|---|
| **Shaffoflik** | 30%–100%, past = shaffofroq | 77% |
| **Har doim ustda** | Boshqa oynalar ustida turadi | O'chirilgan |
| **Ovoz signali** | Namoz vaqtida adhan ohangida signal | Yoqilgan |
| **Mini rejimda boshlanish** | Dastur ochilganda kichik ko'rinishda | Yoqilgan |

### O'ng klik menyusi

Dastur ustida o'ng klik bosing:

- **Sozlamalar** — sozlamalar oynasini ochadi
- **Qayta yuklash** — vaqtlarni internetdan yangilaydi
- **Mini rejim / Kengaytirish** — rejimni almashtiradi
- **Yopish** — dasturni yopadi

---

## 9. Ovoz signallari

| Holat | Signal | Ovoz darajasi |
|---|---|---|
| Namoz vaqti kirdi | Adhan ohangida signal (~7 sekund) | 70% |
| 20 daqiqa qoldi | Bitta yumshoq "ting" | 35% |

**Ovozni o'chirish:** Sozlamalar → "Namoz vaqtida ovozli signal" katagidagi belgini olib tashlang.

**Talablar:** `pygame` va `numpy` kutubxonalari kerak (build.bat o'zi o'rnatadi).

---

## 10. Namoz vaqtlari qanday hisoblanadi?

Dastur **aladhan.com** API dan vaqtlarni oladi:

- **Hisoblash usuli:** Muslim World League (Fajr 18°, Isha 17°)
- **Asr:** Hanafi usuli (soya uzunligi = 2× narsa balandligi)
- **Vaqt zonasi:** Asia/Tashkent (UTC+5)

**Cache tizimi:**

```
Birinchi ishga tushish
  → Internet bor   → API dan yuklanadi → cache.json ga saqlanadi
  → Internet yo'q  → Xato xabari

Keyingi ishga tushishlar
  → cache.json bor → Internetdan yuklanmaydi (tezkor)
  → Sana o'zgardi  → Avtomatik yangi vaqtlar yuklanadi
```

Cache fayllari `D:\Prayer\` papkasida saqlanadi:
- `times_cache.json` — kunlik vaqtlar (14 kun)
- `month_cache.json` — oylik jadval

---

## 11. Taskbardan yashirilgan — qanday topaman?

Dastur taskbarda **ko'rinmaydi** — bu ataylab shunday.

Dastur ekranda suzib yuradi. Agar ko'rinmasa:

1. **Win + D** bosing (ish stoliga o'tish)
2. Dastur odatda ekranning bir chetida turadi
3. Yoki **Task Manager** (Ctrl+Shift+Esc) → Processes → NamozVaqtlari

---

## 12. O'chirish

**Autostartdan o'chirish** (CMD da):
```cmd
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "NamozVaqtlari" /f
```

**Dasturni o'chirish:**
```
D:\Prayer\ papkasini o'chiring
```

---

## 13. Muammolar va yechimlar

**Dastur ochilmayapti**

- `D:\Prayer\NamozVaqtlari.exe` mavjudligini tekshiring
- Antivirus bloklayotgan bo'lishi mumkin → istisnoga qo'shing

**Vaqtlar noto'g'ri**

- Sozlamalar → UMI tuzatish → ISLOM.uz bilan solishtiring
- O'ng klik → Qayta yuklash

**Ovoz eshitilmaydi**

- Sozlamalar → "Ovozli signal" yoqilganligini tekshiring
- Kompyuter ovozi o'chirilmagan bo'lsin

**Internet yo'q, vaqtlar ko'rinmaydi**

- `D:\Prayer\times_cache.json` faylini o'chiring
- Internet ulanib qayta yoqing

**Dastur topilmaydi (ekranda yo'q)**

- Ekran chegarasidan chiqib ketgan bo'lishi mumkin
- Task Manager → NamozVaqtlari → End Task
- Qayta `D:\Prayer\NamozVaqtlari.exe` ni ishga tushiring

---

*Namoz Vaqtlari — O'zbekiston Musulmonlari Idorasi uslubida*