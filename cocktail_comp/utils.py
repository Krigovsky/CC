from .models import GolfGame, GolfCard, Couple

from datetime import datetime
import ast 

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
        couple_names = ast.literal_eval(couple.partner_names)
        # print(couple_names, type(couple_names))

        # inner_list = []
        for name in couple_names:
            # print(name)
            names.append(name)
            if team in drivers:
                drivers[team].append({name : [False for i in range(int(form.cleaned_data["number_holes"]))]})
            else:
                card_drivers.update({team: [False for i in range(int(form.cleaned_data["number_holes"]))]})
                drivers.update({team : [{name: [False for i in range(int(form.cleaned_data["number_holes"]))]}]})
        # names.append(inner_list)
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

    """
    card = {
            # : [0,1,2,3,4,5,6,7,8,9]
            team1 : [0,1,2,3,4,5,6,7,8,9]
            team2 : [0,1,2,3,4,5,6,7,8,9]
            }
    """

def get_team_members(team_name):
    couple = Couple.objects.filter(team=team_name).first()
    names = decode_name(couple.partner_names)
    print(f"Couples name -> {type(names)}")
    return names

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


