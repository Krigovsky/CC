from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.template import loader
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F
from django.views import generic
from django.forms import formset_factory 
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


from .models import Couple, GolfGame, GolfCard, CompetitionStart, Cocktail, CocktailCard, CocktailScores
from .forms import (RegisterForm, StartGolfGameForm, UpdateScoreForm, 
                    UserLoginForm, TeamUpdateForm, StartCompetitionForm,
                    CocktailFormScore, CocktailFormComments, CocktailAddForm,
                    UserRegistrationForm, JoinTeamForm,

                    )

from .utils import (split_names, decode_name, start_new_game, get_team_members, 
                    create_drive_count, get_power_texts, powers_update, 
                    check_previous_holes, create_hide_list, remove_duplicates,
                    start_compeition, create_cocktail_description, gather_total,
                    check_submissions_user, move_to_next_cocktail
                    )

import ast 
import json
from datetime import datetime

# Create your views here.
def index (request):
    if request.method == "POST":
        print("here")
        form = UserRegistrationForm(request.POST)
        if form.is_valid():

            user = User.objects.create_user(first_name=form.cleaned_data["first_name"],
                                            last_name=form.cleaned_data['last_name'],
                                            password=form.cleaned_data['password'],
                                            username=f"{form.cleaned_data["first_name"]}_{form.cleaned_data['last_name']}" )
            print("user created")
            return redirect('cocktail:login')
        
    template = loader.get_template("cocktail/index.html")
    form = UserRegistrationForm()
    context = {
        'form' : form
    }

    return HttpResponse(template.render(context, request))

def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        print("im here")
        if form.is_valid():
            user = authenticate(request, 
                                username=f"{form.cleaned_data["first_name"]}_{form.cleaned_data['last_name']}",
                                password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                print("User is logged in")
                return redirect('cocktail:start')
            else:
                return redirect('cocktail:index')
            
    template = loader.get_template("cocktail/login.html")
    form = UserLoginForm()
    context = {
        'form' : form
    }
    return HttpResponse(template.render(context, request))

def registraition (request):
    print("On registration page")
    template = loader.get_template("cocktail/register.html")
    form = RegisterForm()
    context = { "form":form }
    return HttpResponse(template.render(context, request))

@login_required
def user_management (request, id):

    template = loader.get_template("cocktail/team_management.html")
    teams = Couple.objects.filter().all()
    context = {
        "teams" : teams
    }
    return HttpResponse(template.render(context, request))

@login_required
def create_team (request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("partners chosen ->",form.cleaned_data['partner_names'], "Type -> ", type(form.cleaned_data['partner_names']))
            print("team name -> ", form.cleaned_data['team_name'])
            team = Couple.objects.create(team=form.cleaned_data['team_name'])

            for id in form.cleaned_data['partner_names']:
                team.partner_names.add(id)
                team.save()
            
            print("Partners after adding and savign -> ", team.partner_names.all())

    template = loader.get_template("cocktail/create_team.html")
    form = RegisterForm()

    context = {
        'form' : form 
    }
    return HttpResponse(template.render(context, request))

@login_required
def join_team (request):
    print("Current user -> ", request.user)
    if request.method == "POST":
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            print("team name -> ", form.cleaned_data['team'])
            team = Couple.objects.filter(id=form.cleaned_data['team']).first()
            team.partner_names.add(request.user.id)
            team.save()
            print(team.partner_names.all())


    template = loader.get_template("cocktail/join_team.html")
    form = JoinTeamForm()

    context = {
        'form' : form 
    }
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

            return redirect('cocktail:cocktail_add', id=cpl_session.id)
            

    couples = get_list_or_404(Couple)
    print("Couple -> ", couples, type(couples))
    print("Name -> ", couples[0].team)
    for couple in couples:
        # print(couple.team, '-> ', couple.partner_names, '-> ', type(couple.partner_names))
        couple_name = decode_name(couple.partner_names)
    return render(request, "cocktail/view.html", { "couples" : couples})

# def start_golf (request):
#     print("on start of golf page")
#     template = loader.get_template("cocktail/start_golf.html")
#     form = StartGolfGameForm()
#     context = { "form" : form }
#     return HttpResponse(template.render(context, request))

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
    comp = CompetitionStart.objects.filter(golf_card = golf_card).first()

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
                                         "milligans" : milligans,
                                         "comp_id" : comp.id
                                         }, request))


def go_to_n_hole(request,id, hole):
    print("Going to specfic hole -> ", hole)
    golf_card = GolfCard.objects.filter(id=id).first()

    golf_card.current_hole = hole
    golf_card.save()

    print("Currently set hole ->", golf_card.current_hole)
    return redirect('cocktail:update_score', id=id, hole=golf_card.current_hole)

def teams(request):
    template = loader.get_template("cocktail/teams.html")   

    if 'teams' in request.POST:
        chosen_team_form = TeamUpdateForm(request.POST)
        if chosen_team_form.is_valid():
            
            team = Couple.objects.filter(team=chosen_team_form.cleaned_data["team_name"]).first()
            team_members = get_team_members(team)
            print("team_members -> ", team_members)

            users = User.objects.filter().all()

            teams_form = TeamUpdateForm(initial={
                "old_team" : team.team
            }) 

            form = RegisterForm()

            context = { "form" : form,
                        "teams" : teams_form,
                        "choosen_team" : team,
                        "partner_names" : team_members,
                        "users" : users

                        }
            return HttpResponse(template.render(context, request))
        
    #TODO finish updating team for user and team name 
    if 'update' in request.POST:
        print("Update form submitted")
        form = TeamUpdateForm(request.POST)
        if form.is_valid():
            print("Made it here")
            print("Old team name -> ",form.cleaned_data['old_team'])
        else:
            # <--- THIS IS THE CRUCIAL PART FOR DEBUGGING!
            print("Form is NOT valid!")
            print(form.errors)

    teams_form = TeamUpdateForm() 
    form = RegisterForm()
    context = { "form" : form,
                "teams" : teams_form,
                }
    return HttpResponse(template.render(context, request))

def cocktail_add(request, id):
    print("IN cocktail add. Team ID -> ", id)

    if request.method == "POST":
        form = CocktailAddForm(request.POST)
        
        try:
            cocktail = Cocktail.objects.filter(team_id=id, date=datetime.now())
            print("Cocktail of same team done on the same day")  
        except:
            cocktail = False
            print("No existing cocktials found")

        if form.is_valid() and not cocktail:
            Cocktail.objects.create(
                date = datetime.now(),
                team = Couple.objects.filter(id=id).first(),
                cocktail_name=form.cleaned_data["cocktail_name"],
                alcohol_base=form.cleaned_data["alcohol_base"], 
                mixers=form.cleaned_data["mixers"],             
                garnish=form.cleaned_data["garnish"], 
                total_score = 0
            )
        else:
            print("Cocktail not added into database")
    
    form = CocktailAddForm()
    context = {
        "form" : form,
        "team_id" : id,
    }
    template = loader.get_template("cocktail/cocktail_add.html")
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

def user_display(request, user_id):
    print("in user display -> ", user_id)
    user = User.objects.filter(id=user_id).first()
    print("user -> ", user.id, f' -> {user.first_name} {user.last_name}')

    template = loader.get_template("cocktail/user_display.html")
    
    return HttpResponse(template.render({
        'user_name' : f'{user.first_name} {user.last_name}',
        
    }))

def cocktail (request, id):
    print("Made into cocktail -> ", id)
    comp = CompetitionStart.objects.filter(id = id).first()
    print("Found Comp -> ", comp.cocktail_card.order)

    order = ast.literal_eval(comp.cocktail_card.order)
    teams = ast.literal_eval(comp.teams)

    print('order -> ', order)
    print('teams -> ', teams)

    cocktail_order = [teams[i] for i in order]
    print("Cocktail order = ", cocktail_order)

    context = {
        'order' : cocktail_order,
        'comp_id' : comp.id,
    }

    template = loader.get_template("cocktail/cocktail.html")   
    return HttpResponse(template.render(context, request))

def cocktail_card (request, id, index=0):
    print("Made into cocktail -> ", id)

    if request.method == "POST":

        print("made it here")
        score = CocktailFormScore(request.POST)
        comments = CocktailFormComments(request.POST)
        card = CompetitionStart.objects.filter(id=id).first()
        index = card.cocktail_card.current_index
        if score.is_valid() and comments.is_valid():
            print("current User -> ", request.user.id)
            total_score = gather_total(score)
            if not CocktailScores.objects.filter(submission= request.user,
                                            comp=CompetitionStart.objects.filter(id=id).first(),
                                            index=index).first():
                insert_score = CocktailScores.objects.create(
                    presentation_score=score.cleaned_data['presentation_score'],
                    taste_score = score.cleaned_data['taste_score'],
                    creativity_score = score.cleaned_data['creativity_score'],
                    theme_score = score.cleaned_data['theme_score'],
                    drinkability_score = score.cleaned_data['drinkability_score'],

                    presentation_comments = comments.cleaned_data['presentation_comments'],
                    taste_comments = comments.cleaned_data['taste_comments'],
                    creativity_comments = comments.cleaned_data['creativity_comments'],
                    theme_comments = comments.cleaned_data['theme_comments'],
                    drinkability_comments = comments.cleaned_data['drinkability_comments'],

                    submission = request.user,
                    comp = CompetitionStart.objects.filter(id=id).first(),
                    total = total_score, 
                    index = index
                )
                # card = CompetitionStart.objects.filter(id=id).first()
                # card.cocktail_card.current_index += 1
                # card.cocktail_card.save()
            else:
                print("Already submitted a form for this round")

            return redirect('cocktail:cocktail_joining', id=id)


    form = CocktailFormScore()
    comments = CocktailFormComments()
    descriptions = [
        "How visually appealing is the cocktail?\nConsider: Glassware Choice, garnish creativity/placement, overall aesthetic appeal.",
        "Does the cocktail have a pleasing flavour? is it well-balanced, with no ingredient overpowering the other?\nConsider: Sweetness, sourness, bitterness, saltiness, alcohol intergration, complexity and harmony.",
        "How unique and inventive is the cocktail?\nConsider: uncommon flavour combinations, innovative techniques, originality.",
        "Does the cocktail fit the competition's theme (if applicable)?\nConsider: Is it seasonally or contextually appropriate.",
        "Would you want to drink this agian?\nConsider: Overall enjoyment, ease of drinking (not too strong/weak)",
    ]
    
    comp = CompetitionStart.objects.filter(id=id).first()
    print(comp.teams)
    comp_teams = ast.literal_eval(comp.teams)
    order = ast.literal_eval(comp.cocktail_card.order)
    print("current order -> ", order)
    print("current index -> ", comp.cocktail_card.current_index)

    print(comp_teams[order[comp.cocktail_card.current_index]])

    couple = Couple.objects.filter(team=comp_teams[order[comp.cocktail_card.current_index]]).first()
    print(couple)

    current_cocktail = Cocktail.objects.filter(team=couple.id).first()
    next_up = create_cocktail_description(current_cocktail)

    print(next_up)

    forms = zip(form, comments, descriptions)
    context = {
        'form' : forms,
        'index' : order,
        'id' : id,
        'cocktail_details' : next_up
    }
    template = loader.get_template("cocktail/cocktail_card.html")   
    return HttpResponse(template.render(context, request))

def start_competition (request):
    if request.method == "POST":
        form = StartCompetitionForm(request.POST)

        if form.is_valid():
            print("### Starting Competition form is valid ###")
            start = start_compeition(form)
            return redirect('cocktail:score_card', id=start.golf_card.id, hole=start.golf_card.current_hole)

    form = StartCompetitionForm()
    context = {
        "form" : form
    }
    
    template = loader.get_template("cocktail/start.html")
    return HttpResponse(template.render(context, request))

def cocktail_joining (request, id):
    print("in cocktial joining -> ", id)
    card = CompetitionStart.objects.filter(id=id).first()
    print("current user -> ", request.user)

    # a check if current user gets to this page they have submitted enough to match the index, 
    result = check_submissions_user(id,request.user.id)
    move_next = move_to_next_cocktail(id)
    print("Card current index -> ",card.cocktail_card.current_index)
    print("Submission index from user -> ", result)

    if result == card.cocktail_card.current_index:
        print("In here")
    # if not redirect to cocktail card

    # else keep context to a waiting screen

    # Once everyone has submitted move onto next index in comp
 
    form_sub = CocktailScores.objects.filter(comp = id, submission = request.user.id)
    template = loader.get_template("cocktail/cocktail_join.html")
    context = {

    }
    return HttpResponse(template.render(context, request))
