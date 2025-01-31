from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.template import loader
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic

from .models import Couple, GolfGame, GolfCard
from .forms import RegisterForm, StartGolfGameForm
from .utils import split_names, decode_name, start_new_game
# Create your views here.
def index (request):
    return render(request, "cocktail/index.html")

def registraition (request):
    print("On registration page")
    template = loader.get_template("cocktail/register.html")
    form = RegisterForm()
    context = { "form":form }
    return HttpResponse(template.render(context, request))

def view (request):

    if request.method == "POST":
        print("IN THE IF STATEMENT")
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            print("Name from form -> ", form.cleaned_data["team_name"])
            # print("Partner names -> ", form.cleaned_data["partner_names"], type(form.cleaned_data["partner_names"]))
            names = split_names(form.cleaned_data["partner_names"])
            cpl_session = Couple.objects.create(team=form.cleaned_data["team_name"], partner_names=names)
            

    couples = get_list_or_404(Couple)
    print("Couple -> ", couples, type(couples))
    print("Name -> ", couples[0].team)
    for couple in couples:
        # print(couple.team, '-> ', couple.partner_names, '-> ', type(couple.partner_names))
        couple_name = decode_name(couple.partner_names)
    return render(request, "cocktail/view.html", { "couples" : couples})

def start_golf (request):
    print("on start of golf page")
    template = loader.get_template("cocktail/start_golf.html")
    form = StartGolfGameForm()
    context = { "form" : form }
    return HttpResponse(template.render(context, request))

def golf_card (request):
    print("In golf card space")

    if request.method == "POST":
        form = StartGolfGameForm(request.POST)
        
        if form.is_valid():
            print("Form is valid")
            golf_card = start_new_game(form)

    else:
        start_golf()


    template = loader.get_template("cocktail/game_card.html")
    return HttpResponse(template.render({ "card" : golf_card}, request))

def update_score(request):

    template = loader.get_template("cocktail/update_score.html")
    return HttpResponse(template.render())