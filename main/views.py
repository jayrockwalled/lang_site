from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
from gensim.models import Word2Vec
import re
from gensim.corpora import Dictionary

def urlify(s):
    # Remove all non-word characters (everything except numbers and letters)
    s = re.sub(r"[^\w\s]", '', s)
    # Replace all runs of whitespace with a single dash
    s = re.sub(r"\s+", '-', s)
    return s

class CommChoiceForm(forms.Form):
    CommChoice1 = forms.CharField()
    CommChoice2 = forms.CharField()
    words = forms.CharField()
    submit = forms.CharField(required=False)

def Index(request):
    return render(request,'main/index.html')

def Community(request):
    if request.method == 'POST':
        form = CommChoiceForm(request.POST)
        if form.is_valid():
            CommChoice1 = form.cleaned_data.get('CommChoice1')
            CommChoice2 = form.cleaned_data.get('CommChoice2')
            words = form.cleaned_data.get('words')
            words = urlify(words)

            if CommChoice1 == CommChoice2:
                error = 'Choose two different communities'
                return render(request, template_name='main/error.html', context={'error':error})

            args = [CommChoice1, CommChoice2, words]
            return HttpResponseRedirect(reverse('main:CommView',args = args))
        else:
            return render(request, template_name='main/error.html', context={'error':form.errors})
            
    else:
        form = CommChoiceForm

    return HttpResponseRedirect(reverse('main:CommView'))
        

def CommView(request,choice1,choice2,slug):
    path1 ='C:/Users/josep/Documents/Github/lang_site/main/word2vec/'

    if choice1 == 1:
        wv1 = 'league_word2vec.model'
        comm1_name = 'League'
    elif choice1 == 2:
        wv1 = 'chess_word2vec.model'
        comm1_name = 'Chess'
    elif choice1 == 3:
        wv1 = 'pokemon_word2vec.model'
        comm1_name = 'Pokemon'

    if choice2 == 1:
        wv2 = 'league_word2vec.model'
        comm2_name = 'League'
    elif choice2 == 2:
        wv2 = 'chess_word2vec.model'
        comm2_name = 'Chess'
    elif choice2 == 3:
        wv2 = 'pokemon_word2vec.model'
        comm2_name = 'Pokemon'

    try:
        model1 = Word2Vec.load(path1+wv1, mmap='r')
        most_similar1 = model1.wv.most_similar(slug)
        most_similar1 = most_similar1[0:5]
        freq1 = model1.wv.vocab[slug].count

        model2 = Word2Vec.load(path1+wv2, mmap='r')
        most_similar2 = model2.wv.most_similar(slug)
        most_similar2 = most_similar2[0:5]
        freq2 = model2.wv.vocab[slug].count

    except:
        error = 'That word is not in both communities\' vocabulary.'
        return render(request, template_name='main/error.html', context={'error':error})

    zipped = zip(most_similar1, most_similar2)
    context = {
        'zip': zipped, 
        'freq1':freq1, 
        'freq2':freq2,
        'comm1':comm1_name,
        'comm2':comm2_name
    }
    return render(request, template_name='main/results.html', context=context)