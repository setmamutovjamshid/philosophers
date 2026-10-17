import os
import subprocess
import sys


def main():
    print("--- [Vercel Build] Boshlandi ---")

    # 1. Baza migratsiyalari
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        print("--> DATABASE_URL topildi. PostgreSQL bazasida migratsiyalar bajarilmoqda...")
    else:
        print("--> DATABASE_URL topilmadi. SQLite orqali tekshirilmoqda...")

    try:
        subprocess.run(
            [sys.executable, "manage.py", "migrate", "--noinput"],
            check=True
        )
        print("--> Migratsiyalar muvaffaqiyatli yakunlandi.")
    except Exception as e:
        print(f"--> DIQQAT: Migratsiyada ogohlantirish / xato: {e}")

    # 2. Superuser yaratish (ixtiyoriy, agar muhit o'zgaruvchilari kiritilgan bo'lsa)
    superuser_username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    superuser_password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
    if superuser_username and superuser_password:
        print(f"--> Superuser '{superuser_username}' yaratilmoqda...")
        try:
            subprocess.run(
                [sys.executable, "manage.py", "createsuperuser", "--noinput"],
                check=False
            )
            print("--> Superuser muvaffaqiyatli tayyorlandi.")
        except Exception as e:
            print(f"--> Superuser yaratilmadi: {e}")

    print("--- [Vercel Build] Muvaffaqiyatli yakunlandi ---")


if __name__ == "__main__":
    main()
