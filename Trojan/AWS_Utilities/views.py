from django.http import JsonResponse
from django.shortcuts import render

def test(requests):
    return JsonResponse({'status':'ok'})
