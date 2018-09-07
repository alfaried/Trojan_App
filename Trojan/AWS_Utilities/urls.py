from AWS_Utilities import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.test, name='test'),
    path('ec2/instance/info/', views.getInstanceInfo, name='getInstanceInfo'),
    path('ec2/instance/kill/', views.killInstance, name='killInstance'),
    path('cloudwatch/metric/', views.getCloudWatchMetric, name='getCloudWatchMetric'),
    path('cloudwatch/metric/info/', views.getCloudWatchMetricInfo, name='getCloudWatchMetricInfo'),
]
