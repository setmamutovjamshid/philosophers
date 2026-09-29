from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Choice, Philosopher, Question, Quiz

User = get_user_model()


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
