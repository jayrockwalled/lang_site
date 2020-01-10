from django.shortcuts import render

def Index(request):
    return render(request,'articles/index.html')

def article(request, slug):
    return render(request, 'articles/'+slug+'.html')

def image(request, slug, slug2):
    context = {'slug2': slug2}
    return render(request, template_name='articles/image.html',context=context)