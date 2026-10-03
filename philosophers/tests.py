from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import Aphorism, Choice, Philosopher, Question, Quiz, QuizResult

User = get_user_model()


@override_settings(
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }
)
class PhilosopherViewsTests(TestCase):
    def setUp(self):
        self.p1 = Philosopher.objects.create(
            name='Aflotun (Platon)',
            era='Antik davr',
            birth_death_years='Mil. avv. 427 – 347',
            short_description="Idealar dunyosi va davlat nazariyasi asoschisi.",
            biography="Aflotun Suqrotning eng mashhur shogirdi...",
            famous_quotes="O'zini yengish eng buyuk g'alabadir."
        )

        self.quiz = Quiz.objects.create(
            title="Test 1",
            order=1,
            description="Sinov testi"
        )
        self.question = Question.objects.create(
            quiz=self.quiz,
            order=1,
            text="Falsafaning asosiy savoli nima?",
            explanation="Bu ontologiya va gnoseologiyaning markaziy muammosidir."
        )
        self.choice1 = Choice.objects.create(
            question=self.question,
            text="Moddiy va ruhiy borliq munosabati",
            is_correct=True
        )
        self.choice2 = Choice.objects.create(
            question=self.question,
            text="Faqat matematika",
            is_correct=False
        )

        self.user = User.objects.create_user(
            username='falsafachi',
            email='falsafa@example.com',
            password='Password123'
        )
        self.client.force_login(self.user)

        self.aphorism = Aphorism.objects.create(
            philosopher=self.p1,
            text="Bilim — kuch.",
            is_published=True,
        )

    def test_aphorisms_page_status(self):
        response = self.client.get(reverse('aphorisms'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'philosophers/aphorisms.html')
        self.assertContains(response, 'Bilim — kuch.')
        self.assertContains(response, 'Aflotun')
        self.assertNotContains(response, reverse('philosopher_detail', kwargs={'slug': self.p1.slug}))

    def test_aphorisms_search_by_philosopher_name(self):
        response = self.client.get(reverse('aphorisms') + '?q=Aflotun')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bilim — kuch.')

        response2 = self.client.get(reverse('aphorisms') + '?q=Nomalum')
        self.assertEqual(response2.status_code, 200)
        self.assertNotContains(response2, 'Bilim — kuch.')

    def test_aphorisms_unpublished_hidden(self):
        Aphorism.objects.create(
            philosopher=self.p1,
            text="Yashirin aforizm",
            is_published=False,
        )
        response = self.client.get(reverse('aphorisms'))
        self.assertNotContains(response, 'Yashirin aforizm')

    def test_learn_page_status(self):
        response = self.client.get(reverse('learn'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'philosophers/list.html')
        self.assertContains(response, 'Aflotun')

    def test_detail_page_status(self):
        response = self.client.get(reverse('philosopher_detail', kwargs={'slug': self.p1.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'philosophers/detail.html')
        self.assertContains(response, 'Idealar dunyosi')
        self.assertContains(response, 'eng buyuk')

    def test_tests_page_status(self):
        response = self.client.get(reverse('tests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'philosophers/tests.html')
        self.assertContains(response, 'Test 1')
        self.assertContains(response, '1 ta savol')

    def test_quiz_detail_page_status(self):
        response = self.client.get(reverse('quiz_detail', kwargs={'slug': self.quiz.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'philosophers/quiz_detail.html')
        self.assertContains(response, 'Test 1')
        self.assertContains(response, 'Falsafaning asosiy savoli nima?')

    def test_search_functionality(self):
        response = self.client.get(reverse('learn') + '?q=Aflotun')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aflotun')

        response2 = self.client.get(reverse('learn') + '?q=NomalumFaylasuf')
        self.assertEqual(response2.status_code, 200)
        self.assertNotContains(response2, 'Aflotun')

    def test_admin_changelist_view(self):
        admin_user = User.objects.create_superuser('testadmin', 'testadmin@example.com', 'adminpass123')
        self.client.force_login(admin_user)
        response = self.client.get('/admin/philosophers/philosopher/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aflotun (Platon)')

        # Quiz admin changelist
        response_quiz = self.client.get('/admin/philosophers/quiz/')
        self.assertEqual(response_quiz.status_code, 200)
        self.assertContains(response_quiz, 'Test 1')

    def test_my_results_page_empty(self):
        response = self.client.get(reverse('my_results'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'philosophers/my_results.html')
        self.assertContains(response, 'Hozircha test natijalari mavjud emas')

    def test_submit_quiz_view_creates_result(self):
        import json
        payload = {
            'answers': {'0': 0},  # choice1 is correct (index 0)
            'time_spent_seconds': 45
        }
        url = reverse('submit_quiz', kwargs={'slug': self.quiz.slug})
        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['score'], 1)
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(data['percentage'], 100)

        # Check DB entry
        result = QuizResult.objects.filter(user=self.user, quiz=self.quiz).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.score, 1)
        self.assertEqual(result.percentage, 100)
        self.assertEqual(result.time_spent_seconds, 45)

    def test_my_results_page_with_data(self):
        QuizResult.objects.create(
            user=self.user,
            quiz=self.quiz,
            score=1,
            total_questions=1,
            percentage=100,
            time_spent_seconds=30
        )
        response = self.client.get(reverse('my_results'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test 1')
        self.assertContains(response, '100%')
        self.assertContains(response, "A&#x27;lo")

    def test_my_results_unauthenticated_redirects(self):
        self.client.logout()
        response = self.client.get(reverse('my_results'))
        self.assertEqual(response.status_code, 302)
