from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def Index(request):
    return render(request,'joseph/index.html')