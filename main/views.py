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
import pandas as pd

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
    path1 ='lang_site/main/word2vec/'
    slug = slug.lower()
    if len(slug.split('-')) > 1:
        error = 'Please only enter a single word.'
        return render(request, template_name='main/error.html', context={'error':error})
    
    wv1 = choice1+'_word2vec.model'
    wv2 = choice2+'_word2vec.model'

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

    df1 = pd.read_csv('lang_site/main/tfidf/'+choice1+'_tfidf_df.csv')
    df2 = pd.read_csv('lang_site/main/tfidf/'+choice2+'_tfidf_df.csv')
    tfidf1 = df1[slug].to_string(index=False)
    tfidf2 = df2[slug].to_string(index=False)
    zipped = zip(most_similar1, most_similar2)
    context = {
        'zip': zipped, 
        'freq1':freq1, 
        'freq2':freq2,
        'comm1':choice1,
        'comm2':choice2,
        'tfidf1':tfidf1,
        'tfidf2':tfidf2,
    }
    return render(request, template_name='main/results.html', context=context)