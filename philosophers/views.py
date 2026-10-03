import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Aphorism, Philosopher, Question, Quiz, QuizResult


@login_required
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


@login_required
def philosopher_detail_view(request, slug):
    """Faylasuf haqida barcha batafsil ma'lumotlar sahifasi."""
    philosopher = get_object_or_404(Philosopher, slug=slug)
    quotes = philosopher.quotes_list()

    context = {
        'philosopher': philosopher,
        'quotes': quotes,
    }
    return render(request, 'philosophers/detail.html', context)


@login_required
def aphorisms_view(request):
    """
    Aforizmlar bo'limi: bitta so'rov (select_related + defer og'ir maydonlar).
    Qidiruv: faylasuf ismi bo'yicha filtrlash.
    """
    query = request.GET.get('q', '').strip()

    aphorisms = (
        Aphorism.objects.filter(is_published=True)
        .select_related('philosopher')
        .defer(
            'philosopher__biography',
            'philosopher__main_ideas',
            'philosopher__famous_quotes',
        )
    )

    if query:
        aphorisms = aphorisms.filter(philosopher__name__icontains=query)

    paginator = Paginator(aphorisms, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'aphorisms': page_obj,
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'philosophers/aphorisms.html', context)


@login_required
def tests_view(request):
    """
    'Testlar' bo'limi:
    Admin paneldan kiritilgan Test 1, Test 2... to'plamlarini ko'rsatish.
    Optimizatsiya: annotate orqali savollar sonini 1 ta so'rovda hisoblaydi.
    Foydalanuvchi avval ishlagan quizlar uchun oxirgi natija ham uzatiladi.
    """
    quizzes = Quiz.objects.filter(is_active=True).annotate(
        total_questions=Count('questions')
    ).order_by('order', 'id')

    # Foydalanuvchining har bir quiz uchun oxirgi natijasini topamiz
    # (SQLite va PostgreSQL ikkisida ham ishlaydi)
    all_user_results = QuizResult.objects.filter(
        user=request.user
    ).order_by('-completed_at').select_related('quiz')

    last_result_map = {}
    for r in all_user_results:
        if r.quiz_id not in last_result_map:
            last_result_map[r.quiz_id] = r

    quizzes_with_status = []
    for quiz in quizzes:
        last_result = last_result_map.get(quiz.id)
        quizzes_with_status.append({
            'quiz': quiz,
            'last_result': last_result,
        })

    context = {
        'quizzes': quizzes,
        'quizzes_with_status': quizzes_with_status,
    }
    return render(request, 'philosophers/tests.html', context)


@login_required
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


@login_required
def submit_quiz_view(request, slug):
    """
    Test natijalarini serverda qabul qilish, tekshirish va QuizResult ga saqlash.
    """
    if request.method != 'POST':
        return JsonResponse({'error': "Faqat POST so'rovi qabul qilinadi"}, status=405)

    quiz = get_object_or_404(Quiz, slug=slug, is_active=True)
    questions = list(quiz.questions.prefetch_related('choices').all())

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = {}

    user_answers = data.get('answers', {})
    time_spent_seconds = int(data.get('time_spent_seconds', 0) or 0)

    correct_count = 0
    total_questions = len(questions)
    details = []

    for idx, question in enumerate(questions):
        selected_choice_idx = user_answers.get(str(idx))
        if selected_choice_idx is None:
            selected_choice_idx = user_answers.get(idx)

        choices = list(question.choices.all())
        correct_choice_idx = next((i for i, c in enumerate(choices) if c.is_correct), -1)

        is_correct = (selected_choice_idx is not None and selected_choice_idx == correct_choice_idx)
        if is_correct:
            correct_count += 1

        user_choice_text = (
            choices[selected_choice_idx].text
            if (selected_choice_idx is not None and 0 <= selected_choice_idx < len(choices))
            else "Javob berilmadi"
        )
        correct_choice_text = choices[correct_choice_idx].text if correct_choice_idx != -1 else "Belgilanmagan"

        details.append({
            'question_order': question.order,
            'question_text': question.text,
            'user_choice_idx': selected_choice_idx,
            'user_choice_text': user_choice_text,
            'correct_choice_idx': correct_choice_idx,
            'correct_choice_text': correct_choice_text,
            'is_correct': is_correct,
            'explanation': question.explanation,
        })

    percentage = round((correct_count / total_questions) * 100) if total_questions > 0 else 0

    result = QuizResult.objects.create(
        user=request.user,
        quiz=quiz,
        score=correct_count,
        total_questions=total_questions,
        percentage=percentage,
        time_spent_seconds=time_spent_seconds,
        details=details
    )

    return JsonResponse({
        'success': True,
        'result_id': result.id,
        'score': correct_count,
        'total_questions': total_questions,
        'percentage': percentage,
        'message': "Natijangiz 'Natijalarim' bo'limiga muvaffaqiyatli saqlandi!"
    })


@login_required
def my_results_view(request):
    """
    'Natijalarim' bo'limi:
    Har bir quiz uchun faqat oxirgi (eng so'nggi) natija ko'rsatiladi.
    Urinishlar soni va umumiy statistika ham uzatiladi.
    """
    all_results = QuizResult.objects.filter(user=request.user).select_related('quiz')

    # Umumiy statistika — barcha urinishlar bo'yicha
    stats = all_results.aggregate(
        total_attempts=Count('id'),
        avg_percentage=Avg('percentage'),
        max_percentage=Max('percentage'),
        total_correct=Sum('score'),
        total_questions_sum=Sum('total_questions'),
    )

    total_attempts = stats['total_attempts'] or 0
    avg_percentage = round(stats['avg_percentage']) if stats['avg_percentage'] is not None else 0
    max_percentage = stats['max_percentage'] or 0
    total_correct = stats['total_correct'] or 0
    total_questions_all = stats['total_questions_sum'] or 0

    # Har bir quiz uchun urinishlar soni
    attempts_per_quiz = (
        all_results.values('quiz_id')
        .annotate(attempt_count=Count('id'))
    )
    attempt_count_map = {row['quiz_id']: row['attempt_count'] for row in attempts_per_quiz}

    # Har bir quiz uchun faqat oxirgi natijani olish (Python da filtrlash — SQLite mos)
    last_result_map = {}
    for r in all_results.order_by('-completed_at'):
        if r.quiz_id not in last_result_map:
            last_result_map[r.quiz_id] = r

    # Urinishlar sonini natijaga biriktirish
    unique_results = []
    for result in last_result_map.values():
        result.attempt_count = attempt_count_map.get(result.quiz_id, 1)
        unique_results.append(result)

    # Oxirgi ishlangan vaqt bo'yicha saralash
    unique_results.sort(key=lambda r: r.completed_at, reverse=True)

    # Nechta turli quiz ishlangan
    total_tests = len(unique_results)

    paginator = Paginator(unique_results, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'results': page_obj,
        'page_obj': page_obj,
        'total_tests': total_tests,
        'total_attempts': total_attempts,
        'avg_percentage': avg_percentage,
        'max_percentage': max_percentage,
        'total_correct': total_correct,
        'total_questions': total_questions_all,
    }
    return render(request, 'philosophers/my_results.html', context)
