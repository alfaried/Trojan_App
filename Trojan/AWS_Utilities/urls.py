from AWS_Utilities import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.test, name='test'),
    path('account/info/', views.account_getInfo, name='account_getInfo'),
    path('ec2/dashboard/', views.instance_dashboard, name='instance_dashboard'),
    path('ec2/instance/list/', views.instance_getAll, name='instance_getAll'),
    path('ec2/instance/info/current/', views.instance_getCurentInfo, name='instance_getCurrentInfo'),
    path('ec2/instance/info/', views.instance_getInfo, name='instance_getInfo'),
    path('ec2/volume/list/', views.volume_getAll, name='volume_getAll'),
    path('ec2/volume/info/', views.volume_getInfo, name='volume_getInfo'),
    path('ec2/instance/event/stop/', views.instance_stop, name='instance_stop'),
    path('ec2/instance/event/start/', views.instance_start, name='instance_start'),
    path('cloudwatch/metric/info/', views.cloudwatch_getMetric, name='cloudwatch_getMetric'),
    path('cloudwatch/metric/list/', views.cloudwatch_getAvailableMetrics, name='cloudwatch_getAvailableMetrics'),
    path('elbv2/list/', views.loadbalancerV2_getAll, name='loadbalancerV2_getAll'),
    path('elbv2/info/', views.loadbalancerV2_getInfo, name='loadbalancerV2_getInfo'),
    path('elb/list/', views.loadbalancer_getAll, name='loadbalancer_getAll'),
    path('elb/info/', views.loadbalancer_getInfo, name='loadbalancer_getInfo'),
]
