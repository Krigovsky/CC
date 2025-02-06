from .models import GolfGame, GolfCard, Couple

from datetime import datetime

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
    num = [0 for i in range(int(form.cleaned_data["number_holes"])+1)]
    card = {'#' : [i+1 for i in range(int(form.cleaned_data["number_holes"]))]}
    card["#"].append("Total")

    for player in teams:
        card.update({player : num})


    game_session = GolfGame.objects.create(date = datetime.now(),
                                           game_type=form.cleaned_data["game_type"],
                                           location = form.cleaned_data["location"],
                                           number_holes = form.cleaned_data["number_holes"],
                                           teams_playing = teams
                                           )
    

    game_card = GolfCard.objects.create(card = game_session, 
                                        results = card, 
                                        team_count = len(teams),
                                        score = [0 for i in range(len(game_session.teams_playing))])
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


