from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SignUpTests(TestCase):
    def test_signup_page_status_code(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_successful_signup(self):
        response = self.client.post(reverse('signup'), {
            'full_name': 'Ali Valiyev',
            'username': 'alivaliyev',
            'email': 'ali@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }, follow=True)

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='alivaliyev').exists())
        user = User.objects.get(username='alivaliyev')
        self.assertEqual(user.first_name, 'Ali')
        self.assertEqual(user.last_name, 'Valiyev')
        self.assertEqual(user.email, 'ali@example.com')
        # Check user is logged in
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_short_password_fails(self):
        response = self.client.post(reverse('signup'), {
            'full_name': 'Ali Valiyev',
            'username': 'shortpassuser',
            'email': 'short@example.com',
            'password1': 'Pass1',
            'password2': 'Pass1',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='shortpassuser').exists())
        self.assertFormError(response.context['form'], 'password1', "Parol kamida 8 ta belgidan iborat bo'lishi kerak.")

    def test_duplicate_email_fails(self):
        User.objects.create_user(username='existinguser', email='test@example.com', password='Password123')
        response = self.client.post(reverse('signup'), {
            'full_name': 'Boshqa Odam',
            'username': 'newuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', "Bu email manzili bilan allaqachon hisob ochilgan.")
