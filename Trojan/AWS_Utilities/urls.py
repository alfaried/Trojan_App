from AWS_Utilities import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.test, name='test'),
    path('get_instance_info/', views.getInstanceInfo, name='getInstanceInfo'),
    ath('get_cloudwatch_metric/', views.getInstanceInfo, name='getInstanceInfo'),
    path('kill_instance/', views.killInstance, name='killInstance'),
]
