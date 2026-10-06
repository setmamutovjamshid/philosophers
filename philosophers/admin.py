from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Aphorism, Choice, Philosopher, Question, Quiz, QuizResult


@admin.register(Philosopher)
class PhilosopherAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'era', 'birth_death_years', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name', 'era', 'biography', 'main_ideas', 'short_description')
    list_filter = ('era', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'image_display')

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name', 'slug', 'era', 'birth_death_years', 'image', 'image_display')
        }),
        ("Ta'rif va Tarjimai hol", {
            'fields': ('short_description', 'biography')
        }),
        ("G'oyalari va Iqtiboslari", {
            'fields': ('main_ideas', 'famous_quotes')
        }),
        ("Vaqt belgilari", {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 44px; height: 44px; object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return mark_safe(
            '<div style="width: 44px; height: 44px; background: #f1f5f9; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #94a3b8; font-size: 11px;">Rasm yo\'q</div>'
        )
    image_preview.short_description = "Rasm"

    def image_display(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "Rasm yuklanmagan"
    image_display.short_description = "Joriy rasm"


@admin.register(Aphorism)
class AphorismAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'philosopher', 'is_published', 'order', 'created_at')
    list_editable = ('is_published', 'order')
    list_filter = ('is_published', 'philosopher__era')
    search_fields = ('text', 'philosopher__name')
    autocomplete_fields = ('philosopher',)
    ordering = ('philosopher__name', 'order', '-created_at')

    def text_preview(self, obj):
        return obj.text[:80] + "..." if len(obj.text) > 80 else obj.text
    text_preview.short_description = "Aforizm"


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    min_num = 2
    fields = ('text', 'is_correct')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'quiz', 'order', 'choices_count')
    list_filter = ('quiz',)
    search_fields = ('text', 'explanation')
    ordering = ('quiz', 'order')
    inlines = [ChoiceInline]

    def text_preview(self, obj):
        return obj.text[:70] + "..." if len(obj.text) > 70 else obj.text
    text_preview.short_description = "Savol"

    def choices_count(self, obj):
        return obj.choices.count()
    choices_count.short_description = "Variantlar soni"


class QuestionInline(admin.TabularInline):
    model = Question
    fields = ('order', 'text')
    extra = 0
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'questions_count', 'is_active', 'is_mega_badge', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [QuestionInline]

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('title', 'slug', 'description', 'order', 'is_active')
        }),
        ("⭐ Mega Test sozlamalari", {
            'fields': ('is_mega',),
            'description': (
                "Agar bu testni 'Umumlashtiruvchi Mega Test' sifatida belgilasangiz, "
                "u testlar sahifasida alohida ajralib turuvchi blok sifatida ko'rinadi."
            ),
        }),
    )

    def questions_count(self, obj):
        count = obj.questions.count()
        color = "#10b981" if count >= 10 else "#f59e0b"
        return format_html(
            '<span style="font-weight: bold; color: {};">{} ta savol</span>',
            color, count
        )
    questions_count.short_description = "Savollar soni"

    def is_mega_badge(self, obj):
        if obj.is_mega:
            return mark_safe(
                '<span style="background:#fef3c7;color:#92400e;padding:2px 10px;'
                'border-radius:12px;font-weight:bold;font-size:12px;">🏆 Mega Test</span>'
            )
        return mark_safe('<span style="color:#94a3b8;font-size:12px;">—</span>')
    is_mega_badge.short_description = "Mega?"


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score_display', 'percentage_badge', 'time_display', 'completed_at')
    list_filter = ('quiz', 'completed_at')
    search_fields = ('user__username', 'user__first_name', 'quiz__title')
    readonly_fields = ('user', 'quiz', 'score', 'total_questions', 'percentage', 'time_spent_seconds', 'details', 'completed_at')

    def score_display(self, obj):
        return f"{obj.score} / {obj.total_questions}"
    score_display.short_description = "To'plangan ball"

    def percentage_badge(self, obj):
        color = "#10b981" if obj.percentage >= 80 else ("#3b82f6" if obj.percentage >= 60 else ("#f59e0b" if obj.percentage >= 40 else "#ef4444"))
        return format_html(
            '<span style="font-weight: bold; color: {};">{}%</span>',
            color, obj.percentage
        )
    percentage_badge.short_description = "Foiz"

    def time_display(self, obj):
        return obj.formatted_time
    time_display.short_description = "Sarflangan vaqt"
