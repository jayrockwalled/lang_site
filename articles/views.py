from django.shortcuts import render

def Index(request):
    return render(request,'articles/index.html')