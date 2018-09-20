from AWS_Utilities import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', views.test, name='test'),
    path('account/get/', views.account_getInfo, name='account_getInfo'),
    path('account/keys/add/', views.account_addPublicKey, name='account_addPublicKey'),
    path('account/keys/get/', views.account_getPublicKeys, name='account_getPublicKeys'),
    path('ec2/dashboard/', views.instance_dashboard, name='instance_dashboard'),
    path('ec2/instance/list/', views.instance_getAll, name='instance_getAll'),
    path('ec2/instance/get/current/', views.instance_getCurentInfo, name='instance_getCurrentInfo'),
    path('ec2/instance/get/', views.instance_getInfo, name='instance_getInfo'),
    path('ec2/volume/list/', views.volume_getAll, name='volume_getAll'),
    path('ec2/volume/get/', views.volume_getInfo, name='volume_getInfo'),
    path('ec2/snapshot/list/', views.snapshot_getAll, name='snapshot_getAll'),
    path('ec2/snapshot/get/', views.snapshot_getInfo, name='snapshot_getInfo'),
    path('ec2/image/list/', views.image_getAll, name='image_getAll'),
    path('ec2/image/get/', views.image_getInfo, name='image_getInfo'),
    path('ec2/elastic_ip/list/', views.elasticIP_getAll, name='elasticIP_getAll'),
    path('ec2/elastic_ip/associate/', views.elasticIP_associate, name='elasticIP_associate'),
    path('ec2/instance/event/launch/', views.instance_create, name='instance_create'),
    path('ec2/instance/event/stop/', views.instance_stop, name='instance_stop'),
    path('ec2/instance/event/start/', views.instance_start, name='instance_start'),
    path('ec2/instance/event/terminate/', views.instance_terminate, name='instance_terminate'),
    path('ec2/instance/event/overload/', views.instance_overload, name='instance_overload'),
    path('cloudwatch/metric/list/', views.cloudwatch_getAvailableMetrics, name='cloudwatch_getAvailableMetrics'),
    path('cloudwatch/metric/get/', views.cloudwatch_getMetric, name='cloudwatch_getMetric'),
    path('elbv2/list/', views.loadbalancerV2_getAll, name='loadbalancerV2_getAll'),
    path('elbv2/get/', views.loadbalancerV2_getInfo, name='loadbalancerV2_getInfo'),
    path('elb/list/', views.loadbalancer_getAll, name='loadbalancer_getAll'),
    path('elb/get/', views.loadbalancer_getInfo, name='loadbalancer_getInfo'),
]
