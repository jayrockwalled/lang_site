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
    CommChoice1 = forms.CharField(required=False)
    CommChoice2 = forms.CharField(required=False)
    words = forms.CharField(required=False)
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
            elif not words:
                error = 'Enter a word'
                return render(request, template_name='main/error.html', context={'error':error})


            args = [CommChoice1, CommChoice2, words]
            return HttpResponseRedirect(reverse('main:CommView',args = args))
        else:
            for x in form.errors:
                return HttpResponse(form.errors[x])
            
    else:
        form = CommChoiceForm

    return HttpResponseRedirect(reverse('main:CommView'))
        

def CommView(request,choice1,choice2,slug):
    path1 = 'C:/users/josep/Documents/GitHub/lang_site/main/word2vec/'
    path2 = 'C:/users/josep/Documents/GitHub/lang_site/main/dictionaries/'
    template_name = 'main/results.html'
    result = []

    if choice1 == 1:
        wv1 = 'league_word2vec.model'
        dict1 = 'league_dict.dict'
    elif choice1 == 2:
        wv1 = 'chess_word2vec.model'
        dict1 = 'chess_dict.dict'
    elif choice1 == 3:
        wv1 = 'pokemon_word2vec.model'
        dict1 = 'pokemon_dict.dict'

    if choice2 == 1:
        wv2 = 'league_word2vec.model'
        dict2 = 'league_dict.dict'
    elif choice2 == 2:
        wv2 = 'chess_word2vec.model'
        dict2 = 'chess_dict.dict'
    elif choice2 == 3:
        wv2 = 'pokemon_word2vec.model'
        dict2 = 'pokemon_dict.dict'

    model1 = Word2Vec.load(path1+wv1, mmap='r')
    dictionary1 = Dictionary.load(path2+dict1)

    most_similar1 = model1.wv.most_similar(slug)
    ID1 = dictionary1.token2id[slug]
    freq1 = dictionary1.cfs[ID1]
    result.append(most_similar1)
    result.append(freq1)

    model2 = Word2Vec.load(path1+wv2, mmap='r')
    dictionary2 = Dictionary.load(path2+dict2)

    most_similar2 = model2.wv.most_similar(slug)
    ID2 = dictionary2.token2id[slug]
    freq2 = dictionary2.cfs[ID2]
    result.append(most_similar2)
    result.append(freq2)

    top1_1000 = model1.wv.index2entity[:1000]
    top2_1000 = model2.wv.index2entity[:1000]
    a_set = set(top1_1000)
    b_set = set(top2_1000)
    both = a_set.intersection(b_set)
    f = open('C:/users/josep/Documents/GitHub/lang_site/main/top_1000.txt','r')
    for line in f:
        line = line.replace('\n','')
        if line in both: both.remove(line)
    f.close()

    intersect = len(both)
    result.append(intersect)

    return render(request, template_name=template_name, context={'result':result})