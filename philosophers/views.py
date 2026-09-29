import json
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from .models import Philosopher, Question, Quiz


def philosopher_list_view(request):
    """
    Optimizatsiyalashgan 'O'rganish' bo'limi:
    1. .defer(...) orqali og'ir matnli maydonlar ro'yxatda yuklanmaydi.
    2. Paginator orqali sahifani 12 tadan bo'lib yuklaydi.
    """
    query = request.GET.get('q', '').strip()

    philosophers = Philosopher.objects.defer('biography', 'main_ideas', 'famous_quotes')

    if query:
        philosophers = philosophers.filter(
            Q(name__icontains=query) |
            Q(era__icontains=query) |
            Q(short_description__icontains=query)
        )

    paginator = Paginator(philosophers, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'philosophers': page_obj,
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'philosophers/list.html', context)


def philosopher_detail_view(request, slug):
    """Faylasuf haqida barcha batafsil ma'lumotlar sahifasi."""
    philosopher = get_object_or_404(Philosopher, slug=slug)
    quotes = philosopher.quotes_list()

    context = {
        'philosopher': philosopher,
        'quotes': quotes,
    }
    return render(request, 'philosophers/detail.html', context)


def tests_view(request):
    """
    'Testlar' bo'limi:
    Admin paneldan kiritilgan Test 1, Test 2... to'plamlarini ko'rsatish.
    Optimizatsiya: annotate orqali savollar sonini 1 ta so'rovda hisoblaydi.
    """
    quizzes = Quiz.objects.filter(is_active=True).annotate(
        total_questions=Count('questions')
    ).order_by('order', 'id')

    context = {
        'quizzes': quizzes,
    }
    return render(request, 'philosophers/tests.html', context)


def quiz_detail_view(request, slug):
    """
    Tanlangan test to'plamini yechish sahifasi:
    Prefetch_related orqali barcha 10 ta savol va ularning javob variantlari
    atigi 2 ta SQL so'rovi bilan xotiraga optimal yuklanadi.
    """
    quiz = get_object_or_404(Quiz, slug=slug, is_active=True)
    questions = quiz.questions.prefetch_related('choices').all()

    # Client-side interaktiv ishlash uchun savollar va variantlarni tayyorlash
    questions_data = []
    for q in questions:
        choices_list = []
        correct_index = -1
        for idx, choice in enumerate(q.choices.all()):
            choices_list.append({
                'id': choice.id,
                'text': choice.text,
            })
            if choice.is_correct:
                correct_index = idx

        questions_data.append({
            'id': q.id,
            'order': q.order,
            'text': q.text,
            'explanation': q.explanation,
            'choices': choices_list,
            'correct_index': correct_index,
        })

    context = {
        'quiz': quiz,
        'questions': questions,
        'questions_json': json.dumps(questions_data),
    }
    return render(request, 'philosophers/quiz_detail.html', context)
