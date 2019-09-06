from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms

class CommChoiceForm(forms.Form):
    CommChoice = forms.CharField()

def Index(request):
    return render(request,'main/index.html')

def Community(request):
    if request.method == 'POST':
        form = CommChoiceForm(request.POST)
        if form.is_valid():
            # val = form.cleaned_data.get('CommChoice')
            return HttpResponseRedirect(reverse('main:CommView'))
    else:
        form = CommChoiceForm

    return HttpResponseRedirect(reverse('main:CommView'))
        

def CommView(request):
    return HttpResponse("Test success! You chose")
