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
import request
import boto3
import os
from urllib.request import urlopen

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

        
    s3 = boto3.resource('s3',
         aws_access_key_id='AKIAIQ77Y5D4LAGEMZLA',
         aws_secret_access_key= 'Ndzg4MDUQXgLWPcOwWTUCPwb1TDBfW7063P')
    # url_prefix = 's3://' + 'AKIAIQ77Y5D4LAGEMZLA' + ':' + 'uRJT/Ndzg4MDUQXgLWPcOwWTUCPwb1TDBfW7063P' + "@herokulangsite/"
    url_prefix = 's3://herokulangsite'
    w2v_url_1 = url_prefix+'/w2v/'+choice1+'_word2vec.model'
    w2v_url_2 = url_prefix+'/w2v/'+choice2+'_word2vec.model'
    tfidf_url_1 = url_prefix+'/tfidf/'+choice1+'_tfidf_df.csv'
    tfidf_url_2 = url_prefix+'/tfidf/'+choice2+'_tfidf_df.csv'

    slug = slug.lower()
    if len(slug.split('-')) > 1:
        error = 'Please only enter a single word.'
        return render(request, template_name='main/error.html', context={'error':error})
    
    # wv1 = choice1+'_word2vec.model'
    # wv2 = choice2+'_word2vec.model'

    try:
        # w2v_file1 = urlopen(w2v_url_1)
        model1 = Word2Vec.load(w2v_url_1, mmap='r')
        most_similar1 = model1.wv.most_similar(slug)
        most_similar1 = most_similar1[0:5]
        freq1 = model1.wv.vocab[slug].count

        # w2v_file2 = urlopen(w2v_url_2)
        model2 = Word2Vec.load(w2v_url_2, mmap='r')
        most_similar2 = model2.wv.most_similar(slug)
        most_similar2 = most_similar2[0:5]
        freq2 = model2.wv.vocab[slug].count

    except Exception as e:
        # error = 'That word is not in both communities\' vocabulary.'
        error = str(e)
        return render(request, template_name='main/error.html', context={'error':error})

    # tfidf_file1 = urlopen(tfidf_url_1)
    # tfidf_file2 = urlopen(tfidf_url_2)
    df1 = pd.read_csv(tfidf_url_1)
    df2 = pd.read_csv(tfidf_url_2)
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