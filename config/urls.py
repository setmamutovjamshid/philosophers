from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path, re_path
from django.views.static import serve


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('learn')
    return redirect('signup')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('', include('users.urls')),
    path('', include('philosophers.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

