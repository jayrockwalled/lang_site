from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
from gensim.models import Word2Vec
import re
from gensim.models import KeyedVectors
import pandas as pd
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

    slug = slug.lower()
    if len(slug.split('-')) > 1:
        error = 'Please only enter a single word.'
        return render(request, template_name='main/error.html', context={'error':error})

    s3 = boto3.client('s3')
    # w2v1 = s3.get_object(Bucket='herokulangsite', Key='vectors/'+choice1+'_vectors.kv')
    # w2v2 = s3.get_object(Bucket='herokulangsite', Key='vectors/'+choice2+'_vectors.kv')
    tfidf1 = s3.get_object(Bucket='herokulangsite', Key='tfidf/'+choice1+'_tfidf_df.csv')
    tfidf2 = s3.get_object(Bucket='herokulangsite', Key='tfidf/'+choice2+'_tfidf_df.csv')

    try:
        model1 = KeyedVectors.load('s3://herokulangsite/vectors/'+choice1+'_vectors.kv', mmap='r')
        most_similar1 = model1.most_similar(slug)
        most_similar1 = most_similar1[0:5]

        model2 = KeyedVectors.load('s3://herokulangsite/vectors/'+choice2+'_vectors.kv', mmap='r')
        most_similar2 = model2.most_similar(slug)
        most_similar2 = most_similar2[0:5]

    except Exception as e:
        # error = 'That word is not in both communities\' vocabulary.'
                # Get line
        trace=traceback.extract_tb(sys.exc_info()[2])
        # Add the event to the log
        output ="Error in the server: %s.\n" % (e)
        output+="\tTraceback is:\n"
        for (file,linenumber,affected,line)  in trace:
            output+="\t> Error at function %s\n" % (affected)
            output+="\t  At: %s:%s\n" % (file,linenumber)
            output+="\t  Source: %s\n" % (line)
        output+="\t> Exception: %s\n" % (e)
        return render(request, template_name='main/error.html', context={'error':output})

    df1 = pd.read_csv(tfidf1['Body'])
    df2 = pd.read_csv(tfidf2['Body'])
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