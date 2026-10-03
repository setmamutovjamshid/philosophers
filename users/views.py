from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from .forms import LoginForm, SignUpForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('learn')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            display_name = user.get_full_name() or user.username
            messages.success(
                request,
                f"Xush kelibsiz, {display_name}! Siz muvaffaqiyatli ro'yxatdan o'tdingiz."
            )
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('learn')
        else:
            messages.error(
                request,
                "Formada xatoliklar mavjud. Iltimos, ma'lumotlarni tekshirib qaytadan urinib ko'ring."
            )
    else:
        form = SignUpForm()

    return render(request, 'users/signup.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Foydalanuvchi nomi yoki parol noto'g'ri kiritildi."
        )
        return super().form_invalid(form)


def logout_view(request):
    logout(request)
    messages.info(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
    return redirect('login')


@login_required
def dashboard_view(request):
    context = {
        'user': request.user,
    }
    return render(request, 'users/dashboard.html', context)



@login_required
def make_admin_view(request):
    """
    Render Free versiyasida Shell bo'lmaganda bir martalik admin (superuser) huquqini faollashtirish.
    MUHIM: Bu view faqat .env da ADMIN_SETUP_SECRET o'rnatilgan bo'lsagina ishlaydi.
    """
    expected_secret = getattr(settings, 'ADMIN_SETUP_SECRET', None)

    # Agar .env da secret o'rnatilmagan bo'lsa — xususiyat o'chiq
    if not expected_secret:
        messages.error(request, "Bu xususiyat hozirda faol emas.")
        return redirect('learn')

    secret = request.POST.get('secret', '').strip()
    error = None

    if request.method == 'POST':
        if secret == expected_secret:
            request.user.is_staff = True
            request.user.is_superuser = True
            request.user.save()
            messages.success(
                request,
                f"Tabriklaymiz, @{request.user.username}! Profilingizga Admin (Superuser) maqomi muvaffaqiyatli berildi."
            )
            return redirect('/admin/')
        else:
            error = "Maxfiy kalit noto'g'ri kiritildi!"

    return render(request, 'users/make_admin.html', {'error': error})

