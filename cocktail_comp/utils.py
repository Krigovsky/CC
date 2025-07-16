from .models import GolfGame, GolfCard, Couple, CocktailCard, CompetitionStart
from django.contrib.auth.models import User 

from datetime import datetime
import ast 
import random

def split_names(names):
    name = names.split(', ')
    return name

def decode_name(name_string):
    names = name_string.split(", ")
    final = []

    for x in names:
        final.append(x.strip("''[]"))


    return final

def start_new_game(form):

    teams = []
    for user in form.cleaned_data["teams_playing"]:
        teams.append(user.team)
    # Set amount of holes to be used in dictionary
    num = [0 for i in range(int(form.cleaned_data["number_holes"])+1)]
    # Inizitalise the dictionary with the base line of holes and total
    card = {'#' : [i+1 for i in range(int(form.cleaned_data["number_holes"]))]}
    card["#"].append("Total")
    # Appened the teams name and start scoreing at 0
    for player in teams:
        card.update({player : num})

    
    #drivers
    drivers = {}
    card_drivers = {'#' : [i+1 for i in range(int(form.cleaned_data["number_holes"]))]}
    names = []
    for team in teams:
        couple = Couple.objects.filter(team = team).first()
        print("Couples -> ")
        couple_names = []
        for x in couple.partner_names.all():
            print(x.id)
            user = User.objects.filter(id = x.id).first()
            couple_names.append(f"{user.first_name} {user.last_name}")
        #  ast.literal_eval(couple.partner_names)
        print(couple_names, type(couple_names))

        inner_list = []
        for name in couple_names:
            # print(name)
            names.append(name)
            if team in drivers:
                drivers[team].append({name : [False for i in range(int(form.cleaned_data["number_holes"]))]})
            else:
                card_drivers.update({team: [False for i in range(int(form.cleaned_data["number_holes"]))]})
                drivers.update({team : [{name: [False for i in range(int(form.cleaned_data["number_holes"]))]}]})
        names.append(inner_list)
    powers = {
        "mulligan" : [],
        "milligan" : []
    }

    
    """
    change bool value to true if driver comes back from form at the hole index

    drivers = {
               "Team1" : {player1 : [0,0,0,0,0,0,0,0,0],
                          plater2 : [0,0,0,0,0,0,0,0,0]},
               "Team2" : {player3 : [0,0,0,0,0,0,0,0,0],
                          plater4 : [0,0,0,0,0,0,0,0,0]}
              }
    """


    game_session = GolfGame.objects.create(date = datetime.now(),
                                           game_type=form.cleaned_data["game_type"],
                                           location = form.cleaned_data["location"],
                                           number_holes = form.cleaned_data["number_holes"],
                                           teams_playing = teams
                                           )
    

    game_card = GolfCard.objects.create(card = game_session, 
                                        results = card, 
                                        team_count = len(teams),
                                        score = [0 for i in range(len(game_session.teams_playing))],
                                        driver_count = drivers,
                                        card_driver = card_drivers,
                                        allowed_drivers = names,
                                        powers = powers
                                        )
    return game_card


def get_team_members(team_name):
    
    couple = Couple.objects.filter(team=team_name).first()
    couple_names = []

    for x in couple.partner_names.all():
            print(x.id)
            user = User.objects.filter(id = x.id).first()
            couple_names.append(f"{user.first_name} {user.last_name}")

    return couple_names

def create_drive_count(drivers_dict, card_drivers_dict, current_hole, holes):
    # print("Drivers Drict ->",drivers_dict)
    # print("card_driver Drict ->", card_drivers_dict)
    # print("Number of holes -> ", current_hole)
    over_drivers = []
    for key in drivers_dict.keys():
        for item in drivers_dict[key]:
            for player_key in item.keys():

                for player_item in item[player_key]:
                    if player_item == True:
                        card_drivers_dict[key][current_hole-1] = player_key

                # print("Player count -> ", card_drivers_dict[key].count(player_key))
                if card_drivers_dict[key].count(player_key) >= int(holes/2)+1:
                    over_drivers.append(player_key)
            


    return card_drivers_dict, over_drivers

def get_power_texts(powers, choice):
    print("Inside get power texts")
    text_list = []
    for item in powers[choice]:
        text_list.append(item['text'])
    return text_list


def powers_update(powers, updates, text):
    for item in updates:
        if not powers[text]:
            powers[text].append(item)
        else:
            for dict_item in powers[text]:
                if item["team"] in dict_item["team"]:
                    pass
                else:
                    powers[text].append(item)

    return powers 

def check_previous_holes (powers, teams, hole):
    mull_add_back_in = []
    for index, item in enumerate(powers["mulligan"]):
        if item["hole"] == hole:
            for i in range(len(teams)):
                if teams[i] == item['team']:
                    mull_add_back_in.append(index)
    
    print(powers)
    for item in reversed(mull_add_back_in):
        powers["mulligan"].pop(item)

    #MILLIGANS
    mill_add_back_in = []
    for index, item in enumerate(powers["milligan"]):
        if item["hole"] == hole:
            for i in range(len(teams)):
                if teams[i] == item['team']:
                    mill_add_back_in.append(index)
    
    for item in reversed(mill_add_back_in):
        powers["milligan"].pop(item)

    # print(powers)           
    # print(mill_add_back_in)

    return powers


def create_hide_list (golf_card, teams):
    hide_fields =[]
    # print("\nMulligans")
    for item in golf_card.powers["mulligan"]:
        for i in range(golf_card.team_count):
            # print(item['team'], ' -> ', teams[i])
            if item['team'] == teams[i]:
                # print("IN HERE")
                hide_fields.append(f"id_form-{i}-mulligan")
    
    # print("\nMilligans")
    for item in golf_card.powers["milligan"]:
        for i in range(golf_card.team_count):
            # print(item['team'], ' -> ', teams[i])
            if item['team'] == teams[i]:
                # print("IN HERE")
                hide_fields.append(f"id_form-{i}-milligan")
                hide_fields.append(f"id_form-{i}-milligan_choice")


    return hide_fields


def remove_duplicates(mulligan, powers):
    dups_index = []

    for index, item in enumerate(mulligan):
        print(item)
        if index == 0: 
            continue
        else:
            if mulligan[index]['team'] == powers["mulligan"][index-1]['team']:
                dups_index.append(index)
                print('in here ',powers['mulligan'][index]['team'], ' -> ',powers['mulligan'][index-1]['team']) 
        
    print(dups_index)
    if dups_index:
        for index in reversed(dups_index):      
            powers["mulligan"].pop(index)

    return dups_index

def start_cocktail(form):
    # print("Teams -> ", type(form.cleaned_data["teams_playing"]), form.cleaned_data["teams_playing"])
    # Take team names
    teams = [x.team for x in form.cleaned_data["teams_playing"]]
    random_order = [x for x in range(len(teams))]
    random.shuffle(random_order)

    print('Random order ->',random_order)
    
    cocktail = CocktailCard.objects.create(teams = teams,
                                           presentation_score = [0 for i in range(len(teams))],
                                           presentation_comments = ['' for i in range(len(teams))],

                                           taste_score = [0 for i in range(len(teams))],
                                           taste_comments = ['' for i in range(len(teams))],

                                           creativity_score = [0 for i in range(len(teams))],
                                           creativity_comments = ['' for i in range(len(teams))],

                                           theme_score = [0 for i in range(len(teams))],
                                           theme_comments = ['' for i in range(len(teams))],

                                           drinkability_score = [0 for i in range(len(teams))],
                                           drinkability_comments = ['' for i in range(len(teams))],

                                           total = [0 for i in range(len(teams))],
                                           order = random_order
                                           )
    return cocktail

def start_compeition(form):
    # Create golf variables and db instence
    golf = start_new_game(form)
    # print(golf)

    # Create Cocktail variables and db instence
    cocktail = start_cocktail(form)
    # print(cocktail)

    start = CompetitionStart.objects.create(
        date = datetime.now(),
        teams = [x.team for x in form.cleaned_data["teams_playing"]],
        golf_card = golf,
        cocktail_card = cocktail
    )
    
    return start

def create_cocktail_description(current_cocktail):
    print(type(current_cocktail))
    temp = {
        "Title" : current_cocktail.cocktail_name,
        "Alcohol Base" : current_cocktail.alcohol_base,
        "Mixers" : current_cocktail.mixers,
        "Garnish" : current_cocktail.garnish,
    }
    return temp