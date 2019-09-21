from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
from gensim.models import Word2Vec
import re

def urlify(s):
    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", '', s)
    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '-', s)
    return s

class CommChoiceForm(forms.Form):
    CommChoice = forms.CharField(required=False)
    AnalysisChoice = forms.CharField(required=False)
    words = forms.CharField(required=False)
    submit = forms.CharField(required=False)

def Index(request):
    return render(request,'main/index.html')

def Community(request):
    if request.method == 'POST':
        form = CommChoiceForm(request.POST)
        if form.is_valid():
            CommChoice = form.cleaned_data.get('CommChoice')
            AnalysisChoice = form.cleaned_data.get('AnalysisChoice')
            words = form.cleaned_data.get('words')
            words = urlify(words)

            args = [CommChoice, AnalysisChoice, words]
            return HttpResponseRedirect(reverse('main:CommView',args = args))
        else:
            for x in form.errors:
                return HttpResponse(form.errors[x])
            
    else:
        form = CommChoiceForm

    return HttpResponseRedirect(reverse('main:CommView'))
        

def CommView(request,choice1,choice2,slug):
    path = 'C:/users/josep/desktop/lang_site/main/word2vec/'
    template_name = 'main/results.html'

    if choice1 == 1:
        file_name = 'league_word2vec.model'
    elif choice1 == 2:
        file_name = 'chess_word2vec.model'
    elif choice1 == 3:
        file_name = 'pokemon_word2vec.model'
    model = Word2Vec.load(path+file_name, mmap='r')

    if choice2 == 1:
        result = model.wv.most_similar(slug)
    elif choice2 == 3:
        result = result = model.wv.doesnt_match(slug.split('-'))
    return render(request, template_name=template_name, context={'result':result})