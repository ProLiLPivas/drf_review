from django.urls import path

from . import views


urlpatterns = [
    path('users', views.UsersList.as_view()),
    path('transfer', views.MoneyTransfer.as_view()),
]
