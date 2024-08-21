from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.template import loader
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic

from .models import Couple
from .forms import RegisterForm

# Create your views here.
def index (request):
    return render(request, "cocktail/index.html")

def registraition (request):
    print("On registration page")
    
    form = RegisterForm()
    return render(request, "cocktail/register.html", { "form":form })

def view (request):

    if request.method == "POST":
        print("IN THE IF STATEMENT")
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            print("Name from form -> ", form.cleaned_data["team_name"])
            cpl_session = Couple.objects.create(team=form.cleaned_data["team_name"])
            

        couples = get_list_or_404(Couple)
        print("Couple -> ", couples, type(couples))
        print("Name -> ", couples[0].team)
        return render(request, "cocktail/view.html", { "couples" : couples})
    else:
        return HttpResponse("Problem gone wrong")