from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms

def Index(request):
    return redirect('main:Index')