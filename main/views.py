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
    
    template_name = 'main/results.html'
    result = {}

    if choice1 == 1:
        wv1 = 'league_word2vec.model'
    elif choice1 == 2:
        wv1 = 'chess_word2vec.model'
    elif choice1 == 3:
        wv1 = 'pokemon_word2vec.model'

    if choice2 == 1:
        wv2 = 'league_word2vec.model'
    elif choice2 == 2:
        wv2 = 'chess_word2vec.model'
    elif choice2 == 3:
        wv2 = 'pokemon_word2vec.model'

    model1 = Word2Vec.load(path1+wv1, mmap='r')

    try:
        most_similar1 = model1.wv.most_similar(slug)
        freq1 = model1.wv.vocab[slug].count
        result['Most Similar 1'] = most_similar1
        result['Freq 1'] = freq1

        model2 = Word2Vec.load(path1+wv2, mmap='r')

        most_similar2 = model2.wv.most_similar(slug)
        freq2 = model2.wv.vocab[slug].count
        result['Most Similar 2'] = most_similar2
        result['Freq 2'] = freq2

    except:
        error = 'That word is not in both communities\' vocabulary.'
        return render(request, template_name='main/error.html', context={'error':error})

    # top1_1000 = model1.wv.index2entity[:1000]
    # top2_1000 = model2.wv.index2entity[:1000]
    # a_set = set(top1_1000)
    # b_set = set(top2_1000)
    # both = a_set.intersection(b_set)
    # f = open('C:/users/josep/Documents/GitHub/lang_site/main/top_1000.txt','r')
    # for line in f:
    #     line = line.replace('\n','')
    #     if line in both: both.remove(line)
    # f.close()

    # intersect = len(both)
    # result['Intersection'] = intersect
    zipped = zip(most_similar1, most_similar2)

    return render(request, template_name=template_name, context={'zip': zipped, 'freq1':freq1, 'freq2':freq2})

    # 'zip': zipped
    # 'most_similar_1': most_similar1, 'most_similar_2': most_similar2
    # format of result is a Dictionary
    # result['Most Simialr 1'] = list of 10 most similar words + similarity calc for community 1
    # result['Freq 1'] = int of total frequency of word in community 1
    # repeat for community 2
