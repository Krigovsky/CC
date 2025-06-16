from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.template import loader
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.forms import formset_factory 
from django.forms.models import model_to_dict
from django.contrib.auth.models import User


from .models import Couple, GolfGame, GolfCard
from .forms import RegisterForm, StartGolfGameForm, UpdateScoreForm, UserLoginForm, TeamUpdateForm

from .utils import (split_names, decode_name, start_new_game, get_team_members, 
                    create_drive_count, get_power_texts, powers_update, 
                    check_previous_holes, create_hide_list, remove_duplicates,
                    )

import ast 
import json

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


    # print(f"TEST WORKED | ID = {id} | Hole = {hole}" )
    #Grab the golf card based of the id passed through in the url
    golf_card = GolfCard.objects.filter(id=id).first()
    
    teams = decode_name(golf_card.card.teams_playing)
    #create dynamic form to get the score for the hole
    card_form_set = formset_factory(UpdateScoreForm, extra=golf_card.team_count)
    formset = card_form_set(request.POST or None)


    team_members = []
    for team in teams:
        team_members.append(get_team_members(team))
    
    not_allowed_drivers = ast.literal_eval(golf_card.over_drivers)
    allowed_drivers = ast.literal_eval(golf_card.allowed_drivers)
    drivers = ast.literal_eval(golf_card.driver_count)
    results_dict = ast.literal_eval(golf_card.results)
    card_drivers_dict = ast.literal_eval(golf_card.card_driver)


    for i, form in enumerate(formset):
        available_choices = [(member, member) for member in team_members[i] if member in allowed_drivers]
        form.fields['driver'].choices = available_choices

    mulligan = []
    milligan = []
    powers = ast.literal_eval(golf_card.powers)
    # print("Powers -> ", powers)
    
    if formset.is_valid(): 
        print("##FORM SUBMITTED##")
        count = 0
        for form in formset:
            # print("Milligans -> ",form.cleaned_data.get("milligan"), " -> ", form.cleaned_data.get("milligan_choice"))
            # Updating drivers choice
            for person in drivers[teams[count]]:
                if form.cleaned_data.get("driver") in person:
                    driving = person[form.cleaned_data.get("driver")]
                    driving[golf_card.current_hole-1] = True


            # Updating scores
            team_list = results_dict[teams[count]]
            team_list[golf_card.current_hole - 1] = form.cleaned_data.get("score")
            team_list[-1] += int(form.cleaned_data.get("score")) 

            results_dict[teams[count]] = team_list

            if form.cleaned_data.get("mulligan"):
                mulligan.append({
                    "team" : teams[count],
                    "hole" : golf_card.current_hole,
                    "text" : f"{teams[count]} - Hole {golf_card.current_hole}"
                })
            
            if form.cleaned_data.get("milligan"):
                powers["milligan"].append({
                    "team" : teams[count],
                    "hole" : golf_card.current_hole,
                    "text" : f"{teams[count]} on hole {golf_card.current_hole} used the milligan on {form.cleaned_data.get("milligan_choice")}"
                })

            count += 1 

    
    else:
        print("Something has gone wrong with the form") 
        print(formset.errors)

    print("Checking the scores and drivers")
    print("Drivers -> ", drivers)
    print("Current Hole -> ", golf_card.current_hole-1)
    

    powers = powers_update(powers, mulligan, "mulligan")
    powers = powers_update(powers, milligan, "milligan")

    powers = check_previous_holes(powers, teams, hole)
    print('\n\n')
    remove = remove_duplicates(powers['mulligan'], powers)
    remove = []
    

    print(powers)
    driving_updates, over_drivers = create_drive_count(drivers, card_drivers_dict, golf_card.current_hole, golf_card.card.number_holes)
    not_allowed_drivers.extend(over_drivers)

    # Update the formset with the no drivers no longer able to take drives
    for i, form in enumerate(formset):
        available_choices = [(member, member) for member in team_members[i] if member not in not_allowed_drivers]
        form.fields['driver'].choices = available_choices


    golf_card.powers = powers
    golf_card.over_drivers = not_allowed_drivers
    golf_card.card_driver = driving_updates
    golf_card.driver_count = drivers
    golf_card.results = results_dict
    golf_card.current_hole = hole
    golf_card.save()
    
    hide_fields = create_hide_list(golf_card, teams)

    #Finishing the game once the hole limit is reached
    if golf_card.current_hole > golf_card.card.number_holes:
        
        return redirect('cocktail:score_card', id=id, hole=golf_card.current_hole)

    #final steps
    template = loader.get_template("cocktail/update_score.html")
    return HttpResponse(template.render({
                                         "formset":formset, 
                                         "card" : golf_card, 
                                         "test" :zip(formset, teams),
                                         "number_holes" : golf_card.results['#'],
                                         "hide_json" : json.dumps(hide_fields)
                                         }, request))

def score_card (request, id, hole):
    #Grab the golf card based of the id passed through in the url
    golf_card = GolfCard.objects.filter(id=id).first()
    results_dict = ast.literal_eval(golf_card.results)
    
    card_drivers_dict = ast.literal_eval(golf_card.card_driver)
    for key in card_drivers_dict.keys():
        
        for index, item in enumerate(card_drivers_dict[key]):
            if not item:
                card_drivers_dict[key][index] = "-"
    
    powers = ast.literal_eval(golf_card.powers)
    mulligans = get_power_texts(powers, "mulligan")
    
    milligans = get_power_texts(powers, "milligan")

    template = loader.get_template("cocktail/game_card.html")   
    return HttpResponse(template.render({ "card" : golf_card,
                                         "results" : results_dict,
                                         "drives" : card_drivers_dict,
                                         "mulligans" : mulligans,
                                         "milligans" : milligans
                                         }, request))


def go_to_n_hole(request,id, hole):
    print("Going to specfic hole -> ", hole)
    golf_card = GolfCard.objects.filter(id=id).first()

    golf_card.current_hole = hole
    golf_card.save()

    print("Currently set hole ->", golf_card.current_hole)
    return redirect('cocktail:update_score', id=id, hole=golf_card.current_hole)

def teams(request):
    if 'teams' in request.POST:
        chosen_team_form = TeamUpdateForm(request.POST)
        if chosen_team_form.is_valid():

            print("team chosen to edit -> ", chosen_team_form.cleaned_data["team_name"])

    template = loader.get_template("cocktail/teams.html")   
    teams_form = TeamUpdateForm() 
    # for item in teams:
    #     print(item, item.partner_names)
    form = RegisterForm()
    context = { "form" : form,
                "teams" : teams_form 
                }
    return HttpResponse(template.render(context, request))

def user_registraition(request):

    if request.method == "POST":
        print("form is recived")
        form = UserLoginForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data['first_name'])
            user = User.objects.filter(username = f"{form.cleaned_data['first_name']}_{form.cleaned_data['last_name']}").first()
            if not user:
                user = User.objects.create_user(first_name = form.cleaned_data['first_name'],
                                                last_name = form.cleaned_data['last_name'],
                                                username= f"{form.cleaned_data['first_name']}_{form.cleaned_data['last_name']}",
                                                password = form.cleaned_data['password'],
                                                )
                print(user.password)
            else:
                print(user.password, ' -> ', user.id)

            return redirect('cocktail:user_display', user_id = user.id)
           

    form = UserLoginForm()
    template = loader.get_template("cocktail/user-register.html")
    return HttpResponse(template.render({"form": form}, request))


def login(request):

    if request.method == "POST":
        print("form is recived")
        form = UserLoginForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data['first_name'])
            check = User.objects.filter(username = f"{form.cleaned_data['first_name']}_{form.cleaned_data['last_name']}")
            if not check:
                user = User.objects.create_user(first_name = form.cleaned_data['first_name'],
                                                last_name = form.cleaned_data['last_name'],
                                                username= f"{form.cleaned_data['first_name']}_{form.cleaned_data['last_name']}",
                                                password = form.cleaned_data['password'],
                                                )
                print(user.password)
            else:
                print(check[0].password)
           

    form = UserLoginForm()
    template = loader.get_template("cocktail/login.html")
    return HttpResponse(template.render({"form": form}, request))

def user_display(request, user_id):
    print("in user display -> ", user_id)
    user = User.objects.filter(id=user_id).first()
    print("user -> ", user.id, f' -> {user.first_name} {user.last_name}')

    template = loader.get_template("cocktail/user_display.html")
    
    return HttpResponse(template.render({
        'user_name' : f'{user.first_name} {user.last_name}',
        
    }))


def start_cocktail (request):
    template = loader.get_template("cocktail/cocktail_start.html")   
    return HttpResponse(template.render())