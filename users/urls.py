from django.urls import path
from .views import (
    CustomLoginView,
    dashboard_view,
    logout_view,
    make_admin_view,
    signup_view,
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('make-admin/', make_admin_view, name='make_admin'),
]

