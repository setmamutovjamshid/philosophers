from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from .forms import LoginForm, SignUpForm


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

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
            return redirect('dashboard')
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
    return render(request, 'users/dashboard.html', {'user': request.user})
