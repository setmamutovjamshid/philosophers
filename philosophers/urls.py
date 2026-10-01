from django.urls import path
from .views import (
    my_results_view,
    philosopher_detail_view,
    philosopher_list_view,
    quiz_detail_view,
    submit_quiz_view,
    tests_view,
)

urlpatterns = [
    path('learn/', philosopher_list_view, name='learn'),
    path('learn/<slug:slug>/', philosopher_detail_view, name='philosopher_detail'),
    path('tests/', tests_view, name='tests'),
    path('tests/<slug:slug>/', quiz_detail_view, name='quiz_detail'),
    path('tests/<slug:slug>/submit/', submit_quiz_view, name='submit_quiz'),
    path('my-results/', my_results_view, name='my_results'),
]
