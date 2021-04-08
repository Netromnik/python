from django.shortcuts import render

# Create your views here.
def Index(request):
    print("Hellow worlsd")
    return  render(request,'mod_news/index.html')