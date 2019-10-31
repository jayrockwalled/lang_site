from django.shortcuts import render

def Index(request):
    return render(request,'articles/index.html')

def article(request, slug):
    return render(request, 'articles/'+slug+'.html')