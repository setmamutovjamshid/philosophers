from django.urls import path
from .views import (
    philosopher_detail_view,
    philosopher_list_view,
    quiz_detail_view,
    tests_view,
)

urlpatterns = [
    path('learn/', philosopher_list_view, name='learn'),
    path('learn/<slug:slug>/', philosopher_detail_view, name='philosopher_detail'),
    path('tests/', tests_view, name='tests'),
    path('tests/<slug:slug>/', quiz_detail_view, name='quiz_detail'),
]
