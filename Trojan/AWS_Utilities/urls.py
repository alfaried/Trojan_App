from AWS_Utilities import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.test, name='test'),
]
