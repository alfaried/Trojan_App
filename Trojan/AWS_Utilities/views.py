import boto3
import requests
from django.http import JsonResponse
from django.shortcuts import render
from Trojan.settings import PUBLIC_IP

def test(request):
    return JsonResponse({'status':'ok'})

def killInstance(request):
    response = {'status':'ok'}

    httpresponse = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    instance_id = httpresponse.text
    response['instance_id'] = instance_id

    return JsonResponse(response)

def getInstanceInfo(request):
    response = {'status':'ok'}

    return JsonResponse(response)
