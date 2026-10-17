# Vercel'ga Joylash (Deployment) Bo'yicha To'liq Qo'llanma

Ushbu Django loyihasi Vercel serverless platformasiga to'liq moslashtirildi.

---

## 1. Loyihada Nimalar Tayyorlandi?

1. **`vercel.json`** — Vercel uchun serverless konfiguratsiya yaratildi (build komandasi va WSGI entrypoint belgilandi).
2. **`build.py`** — Vercel'da deploy paytida ma'lumotlar bazasi migratsiyalarini (`migrate`) avtomatik bajaruvchi skript tayyorlandi.
3. **`config/wsgi.py`** — Vercel serverless funksiyalari uchun `app = application` moslashuvi qo'shildi.
4. **`config/settings.py`** — `.vercel.app` domenlari `ALLOWED_HOSTS` va `CSRF_TRUSTED_ORIGINS` ga kiritildi (CSRF 403 va DisallowedHost xatolarining oldi olindi).
5. **`.gitignore`** va **`.env.example`** — Vercel va maxfiy ma'lumotlar uchun yangilandi.

---

## 2. Muhim: Baza va Media Fayllar

Vercel **serverless** arxitekturada ishlaydi (har bir so'rovdan so'ng vaqtinchalik xotira tozalanadi). Shu sababli:
- **Ma'lumotlar bazasi (Database):** Serverda SQLite ishlatilmaydi, doimiy saqlanadigan bepul tashqi PostgreSQL bazasi kerak:
  - Tavsiya: [Neon.tech](https://neon.tech) yoki [Supabase.com](https://supabase.com) (ro'yxatdan o'tib, bepul PostgreSQL oching va `DATABASE_URL` havolasini oling).
- **Rasmlar (Media):** Yangi rasm yuklashlar uchun bepul [Supabase Storage](https://supabase.com) S3-mos xotira ulanishi tavsiya etiladi (loyihada bunga tayyor kod mavjud).

---

## 3. Vercel'ga Joylash Qadamlari

### 1-USUL: GitHub orqali (Eng qulay va tavsiya etiladigan usul)

1. Loyiha papkasida Git repozitoriya oching va GitHub'ga yuklang:
   ```bash
   git init
   git add .
   git commit -m "Vercel deployment setup"
   git branch -M main
   # GitHub'da yangi repozitoriya ochib, uning havolasini ulang:
   git remote add origin https://github.com/USERNAME/REPO_NAME.git
   git push -u origin main
   ```

2. [Vercel.com](https://vercel.com) saytiga kiring va GitHub profilingiz orqali kiring.
3. **"Add New..."** -> **"Project"** tugmasini bosing.
4. GitHub'ga yuklagan repozitoriyangizni topib, **"Import"** tugmasini bosing.
5. **"Environment Variables"** bo'limini oching va quyidagi o'zgaruvchilarni qo'shing:

| O'zgaruvchi nomi (Key) | Misol qiymat (Value) | Izoh |
|---|---|---|
| `SECRET_KEY` | `django-insecure-kuchli-tasodifiy-kalit-yozing-987` | Django xavfsizlik kaliti |
| `DEBUG` | `False` | Ishchi rejim |
| `DATABASE_URL` | `postgresql://user:pass@ep-xyz.neon.tech/neondb?sslmode=require` | Neon yoki Supabase PostgreSQL havolasi |
| `ADMIN_SETUP_SECRET` | `mening_maxfiy_parolim_123` | Saytdan o'zingizga admin huquqi berish uchun |

*(Agar Supabase Storage ulasangiz: `SUPABASE_STORAGE_ENDPOINT`, `SUPABASE_STORAGE_BUCKET`, `SUPABASE_STORAGE_ACCESS_KEY`, `SUPABASE_STORAGE_SECRET_KEY` larni ham qo'shing).*

6. **"Deploy"** tugmasini bosing. Bir necha daqiqada loyihangiz global serverga joylanadi va sizga `https://...vercel.app` ko'rinishidagi havola beriladi!

---

### 2-USUL: Vercel CLI orqali (Terminaldan to'g'ridan-to'g'ri)

1. Node.js o'rnatilgan bo'lsa, terminalda buyruqni bering:
   ```bash
   npx vercel
   ```
2. So'rovlarga javob bering:
   - `Set up and deploy?` -> **Y**
   - `Which scope?` -> Sizning akkauntingiz
   - `Link to existing project?` -> **N**
   - `What's your project's name?` -> `philosophers` (yoki xohlagan nom)
   - `In which directory is your code located?` -> `./`
3. Environment variables qo'shish uchun:
   ```bash
   npx vercel env add DATABASE_URL production
   npx vercel env add SECRET_KEY production
   npx vercel env add ADMIN_SETUP_SECRET production
   ```
4. Production rejimida qayta deploy qilish:
   ```bash
   npx vercel --prod
   ```

---

## 4. Saytda Admin (Superuser) Huquqini Faollashtirish

Vercel serverless bo'lgani sababli to'g'ridan-to'g'ri SSH terminal yo'q. Loyihangizda xavfsiz web-admin yaratish funksiyasi mavjud:

1. Deploy bo'lgan saytingizga kiring (masalan: `https://philosophers.vercel.app/signup/`).
2. Yangi oddiy hisob oching va tizimga kiring.
3. Brauzerda quyidagi manzilga o'ting:
   ```
   https://sizning-saytingiz.vercel.app/make-admin/
   ```
4. Vercel Environment Variables'da kiritgan `ADMIN_SETUP_SECRET` parolingizni kiriting.
5. Bir lahzada profilingizga to'liq **Admin (Superuser)** maqomi beriladi va avtomatik `/admin/` paneliga yo'naltirilasiz!
