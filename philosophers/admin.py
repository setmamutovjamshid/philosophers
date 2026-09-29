from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Choice, Philosopher, Question, Quiz


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
    list_display = ('title', 'order', 'questions_count', 'is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [QuestionInline]

    def questions_count(self, obj):
        count = obj.questions.count()
        color = "#10b981" if count >= 10 else "#f59e0b"
        return format_html(
            '<span style="font-weight: bold; color: {};">{} ta savol</span>',
            color, count
        )
    questions_count.short_description = "Savollar soni"
