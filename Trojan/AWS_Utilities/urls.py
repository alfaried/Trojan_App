from AWS_Utilities import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.test, name='test'),
    path('ec2/instance/info/', views.instance_getInfo, name='instance_getInfo'),
    path('ec2/instance/stop/', views.instance_stop, name='instance_stop'),
    path('cloudwatch/metric/', views.cloudwatch_getMetricInfo, name='cloudwatch_getMetricInfo'),
    path('cloudwatch/metric/list/', views.cloudwatch, name='cloudwatch'),
]
