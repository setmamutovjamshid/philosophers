from django.db import models
from django.utils.text import slugify


class Philosopher(models.Model):
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name="Faylasufning ismi"
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        db_index=True,
        verbose_name="Slug (havola uchun)",
        help_text="Bo'sh qoldirilsa, ismdan avtomatik shakllantiriladi."
    )
    era = models.CharField(
        max_length=150,
        blank=True,
        db_index=True,
        verbose_name="Davri / Falsafiy oqimi",
        help_text="Masalan: Antik davr, Sharq Renessansi, Ratsionalizm, Ma'rifatparvarlik..."
    )
    birth_death_years = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Yashagan yillari",
        help_text="Masalan: Mil. avv. 470 - 399 yoki 980 - 1037"
    )
    image = models.ImageField(
        upload_to='philosophers/',
        blank=True,
        null=True,
        verbose_name="Faylasuf rasmi"
    )
    short_description = models.CharField(
        max_length=400,
        blank=True,
        verbose_name="Qisqacha ta'rif",
        help_text="Ro'yxatda ko'rinadigan qisqacha ma'lumot"
    )
    biography = models.TextField(
        verbose_name="Batafsil ma'lumot (Tarjimai hol va faoliyati)"
    )
    main_ideas = models.TextField(
        blank=True,
        verbose_name="Asosiy falsafiy g'oyalari va ta'limoti"
    )
    famous_quotes = models.TextField(
        blank=True,
        verbose_name="Mashhur iqtiboslari",
        help_text="Har bir iqtibosni yangi qatordan yozishingiz mumkin."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Kiritilgan vaqt"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Oxirgi tahrir"
    )

    class Meta:
        verbose_name = "Faylasuf"
        verbose_name_plural = "Faylasuflar"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['era']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Philosopher.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def quotes_list(self):
        """Iqtiboslarni qatorlar bo'yicha ro'yxat qilib qaytaradi."""
        if not self.famous_quotes:
            return []
        return [q.strip() for q in self.famous_quotes.split('\n') if q.strip()]


class Quiz(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Test to'plami nomi",
        help_text="Masalan: Test 1, Test 2: Antik davr falsafasi..."
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        db_index=True,
        verbose_name="Slug (havola uchun)"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Test haqida qisqacha ma'lumot",
        help_text="Ushbu test qaysi mavzularni qamrab olgani haqida qisqa tushuntirish."
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="Tartib raqami",
        help_text="Chiqish tartibi (1, 2, 3...)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faolmi?",
        help_text="Belgilansa, saytda foydalanuvchilarga ko'rinadi."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqt"
    )

    class Meta:
        verbose_name = "Test to'plami"
        verbose_name_plural = "Test to'plamlari"
        ordering = ['order', 'id']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "test"
            slug = base_slug
            counter = 1
            while Quiz.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def question_count(self):
        return self.questions.count()


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Tegishli test to'plami"
    )
    text = models.TextField(
        verbose_name="Savol matni"
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="Savol tartibi",
        help_text="Masalan: 1 dan 10 gacha"
    )
    explanation = models.TextField(
        blank=True,
        verbose_name="Javob izohi / tushuntirish",
        help_text="Foydalanuvchi javob berganidan keyin ko'rsatiladigan ma'lumot"
    )

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.quiz.title} - {self.order}-savol: {self.text[:50]}"


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name="Savol"
    )
    text = models.CharField(
        max_length=400,
        verbose_name="Javob varianti"
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name="To'g'ri javob",
        help_text="Ushbu variant to'g'ri bo'lsa belgilang"
    )

    class Meta:
        verbose_name = "Javob varianti"
        verbose_name_plural = "Javob variantlari"

    def __str__(self):
        status = " [To'g'ri]" if self.is_correct else ""
        return f"{self.text}{status}"
