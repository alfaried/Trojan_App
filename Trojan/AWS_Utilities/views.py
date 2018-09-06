import boto3
from django.http import JsonResponse
from django.shortcuts import render
from Trojan.settings import PUBLIC_IP
from AWS_Utilities.src.aws_utils import *

def test(request):
    response = {'status':'OK', 'code':'200'}
    return JsonResponse(response)

def killInstance(request):
    response = {'status':'OK', 'code':'200'}

    instance_id = getInstanceID()
    ec2 = boto3.client('ec2')

    # Do a dryrun first to verify permissions
    try:
        ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        response['status'] = 'Unauthorized'
        response['code'] = '401'
        response['message'] = 'Dry run failed'
        response['error'] = e.args[0]

    # Dry run succeeded, call stop_instances without dryrun
    try:
        results = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
        response.update(results)
    except ClientError as e:
        response['status'] = 'Bad request'
        response['code'] = '400'
        response['error'] = e.args[0]

    return JsonResponse(response)

def getInstanceInfo(request):
    response = {'status':'OK', 'code':'200'}
    return JsonResponse(response)
