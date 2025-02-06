from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.template import loader
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.forms import formset_factory 
from django.forms.models import model_to_dict


from .models import Couple, GolfGame, GolfCard
from .forms import RegisterForm, StartGolfGameForm, UpdateScoreForm
from .utils import split_names, decode_name, start_new_game, get_team_members

import ast 

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
    print("Creating the card")

    if request.method == "POST":
        form = StartGolfGameForm(request.POST)
        
        if form.is_valid():
            print("Form is valid")
            golf_card = start_new_game(form)

    #pass the id of golf card into the url of the score card page
    return redirect('cocktail:score_card', id=golf_card.id, hole=golf_card.current_hole)

def update_score(request, id, hole):


    print(f"TEST WORKED | ID = {id} | Hole = {hole}" )
    #Grab the golf card based of the id passed through in the url
    golf_card = GolfCard.objects.filter(id=id).first()
    
    teams = decode_name(golf_card.card.teams_playing)
    #create dynamic form to get the score for the hole
    card_form_set = formset_factory(UpdateScoreForm, extra=golf_card.team_count)
    formset = card_form_set(request.POST or None)
    team_members = []
    for team in teams:
        team_members.append(get_team_members(team))
    
    print("Team Members -> ", team_members)

    for i, form in enumerate(formset):
        form.fields['driver'].choices = [(member, member) for member in team_members[i]]

    results_dict = ast.literal_eval(golf_card.results)
    # score_list = ast.literal_eval(golf_card.score)
    # print("Score list -> ", score_list, type(score_list))
    if formset.is_valid(): 
        print("##FORM SUBMITTED##")
        hole = int(request.POST.get("hole"))
        print("Hole -> ", hole)
        count = 0
        for form in formset:   
            # score_list[count] += int(form.cleaned_data.get("score"))
            print(results_dict)          
            team_list = results_dict[teams[count]]
            team_list[golf_card.current_hole - 1] = form.cleaned_data.get("score")
            team_list[-1] += int(form.cleaned_data.get("score")) 
            print(f"Score - > {form.cleaned_data.get("score")}")

            results_dict[teams[count]] = team_list

            count += 1        

    print(results_dict)

    # golf_card.score = score_list
    golf_card.results = results_dict
    
    #update Current hole 
    golf_card.current_hole = hole
    golf_card.save()
    
    #Finishing the game once the hole limit is reached
    if golf_card.current_hole > golf_card.card.number_holes:
        
        return redirect('cocktail:score_card', id=id, hole=golf_card.current_hole)

    #final steps
    template = loader.get_template("cocktail/update_score.html")
    return HttpResponse(template.render({
                                         "formset":formset, 
                                         "card" : golf_card, 
                                         "test" :zip(formset, teams),
                                         "number_holes" : golf_card.results['#']
                                         }, request))

def score_card (request, id, hole):
    #Grab the golf card based of the id passed through in the url
    golf_card = GolfCard.objects.filter(id=id).first()
    print(golf_card)
    results_dict = ast.literal_eval(golf_card.results)

    template = loader.get_template("cocktail/game_card.html")   
    return HttpResponse(template.render({ "card" : golf_card,
                                         "results" : results_dict
                                         }, request))


def go_to_n_hole(request,id, hole):
    print("Going to specfic hole -> ", hole)
    golf_card = GolfCard.objects.filter(id=id).first()

    golf_card.current_hole = hole
    golf_card.save()

    print("Currently set hole ->", golf_card.current_hole)
    return redirect('cocktail:update_score', id=id, hole=golf_card.current_hole)

