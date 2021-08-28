import requests
import json

def get_teams_data():
    teams = { "teams": [] }

    data = requests.get("https://api.sofascore.com/api/v1/unique-tournament/170/season/37053/standings/total").json()["standings"][0]["rows"]

    for team in data:
        teams["teams"].append({ "name": team["team"]["shortName"], 
                                "abbr": team["team"]["nameCode"], 
                                "id": team["team"]["id"] })

    with open("teams.json", "w") as file:
        json.dump(teams, file, indent=4)

def get_match_data():
    matches = { "matches": [] }

    with open("teams.json") as file:
        teams = json.load(file)

    data = requests.get("https://api.sofascore.com/api/v1/unique-tournament/170/season/37053/team-events/total").json()["tournamentTeamEvents"]["48"]

    for team in teams["teams"]:
        for match in data[str(team["id"])]:
            if(match["status"]["type"] == "finished"):
                matches["matches"].append({ "homeTeam": match["homeTeam"]["nameCode"], 
                                            "homeScore": match["homeScore"]["display"], 
                                            "awayTeam": match["awayTeam"]["nameCode"], 
                                            "awayScore": match["awayScore"]["display"], 
                                            "startTimestamp": match["startTimestamp"], 
                                            "winnerCode": match["winnerCode"], 
                                            "id": match["id"] })

    with open("matches.json", "w") as file:
        json.dump(matches, file, indent=4)

def get_incident_data():
    incidents = { "incidents" : {} }
    
    with open("matches.json") as file:
        matches = json.load(file)

    for match in matches["matches"]:
        data = requests.get("https://api.sofascore.com/api/v1/event/" + str(match["id"]) + "/incidents").json()["incidents"]
        incidents["incidents"][str(match["id"])] = []
        for incident in data:
            if incident["incidentType"] == "period":
                pass
            elif incident["incidentType"] == "substitution":
                incidents["incidents"][str(match["id"])].append({ "playerIn": incident["playerIn"]["id"], "playerOut": incident["playerOut"]["id"], "time": incident["time"], "incidentType": "substitution" })
            elif incident["incidentType"] == "card":
                incidents["incidents"][str(match["id"])].append({ "player": incident["player"]["id"], "card": incident["incidentClass"], "time": incident["time"], "incidentType": "card" })
            elif incident["incidentType"] == "goal":
                try:
                    assist = incident["assist1"]["id"]
                except:
                    assist = "N/A"
                incidents["incidents"][str(match["id"])].append({ "goalscorer": incident["player"]["id"], "assist": assist, "time": incident["time"], "incidentType": "goal" })

    with open("incidents.json", "w") as file:
        json.dump(incidents, file, indent=4)

def get_player_data():
    players = { "players" : {} }
    
    with open("teams.json") as file:
        teams = json.load(file)

    for team in teams["teams"]:
        data = requests.get("https://api.sofascore.com/api/v1/team/" + str(team["id"]) + "/players").json()["players"]
        players["players"][str(team["id"])] = []
        for player in data:
            try: 
                position = player["player"]["position"]
            except:
                position = "N/A"

            try: 
                country = player["player"]["country"]["alpha2"]
            except:
                country = "N/A"

            players["players"][str(team["id"])].append({"name": player["player"]["name"], 
                                                        "shortName": player["player"]["shortName"], 
                                                        "position": position,
                                                        "country": country, 
                                                        "id": player["player"]["id"] })

    with open("players.json", "w") as file:
        json.dump(players, file, indent=4)

def get_lineup_data():
    lineups = {"lineups": {}}

    with open("matches.json") as file:
        matches = json.load(file)

    for match in matches["matches"]:
        data = requests.get("https://api.sofascore.com/api/v1/event/" + str(match["id"]) + "/lineups").json()
        lineups["lineups"][str(match["id"])] = { "home": [], "away": [] }
        for player in data["home"]["players"]:

            try:
                minutesPlayed = player["statistics"]["minutesPlayed"]
            except:
                minutesPlayed = 0

            if minutesPlayed != 0:
                if player["position"] == "G":
                    try:
                        saves = player["statistics"]["saves"]
                    except:
                        saves = 0
                    lineups["lineups"][str(match["id"])]["home"].append({ "id": player["player"]["id"], 
                                                                        "minutesPlayed": minutesPlayed, 
                                                                        "saves": saves, 
                                                                        "substitute": player["substitute"] })
                else: 
                    lineups["lineups"][str(match["id"])]["home"].append({ "id": player["player"]["id"], 
                                                                        "minutesPlayed": minutesPlayed, 
                                                                        "substitute": player["substitute"] })

        for player in data["away"]["players"]:

            try:
                minutesPlayed = player["statistics"]["minutesPlayed"]
            except:
                minutesPlayed = 0

            if minutesPlayed != 0:
                if player["position"] == "G":
                    try:
                        saves = player["statistics"]["saves"]
                    except:
                        saves = 0
                    lineups["lineups"][str(match["id"])]["away"].append({ "id": player["player"]["id"], 
                                                                        "minutesPlayed": (player["statistics"]["minutesPlayed"] if player["statistics"] != {} else 0), 
                                                                        "saves": saves, 
                                                                        "substitute": player["substitute"] })
                else: 
                    lineups["lineups"][str(match["id"])]["away"].append({ "id": player["player"]["id"], 
                                                                        "minutesPlayed": minutesPlayed, 
                                                                        "substitute": player["substitute"] })

    with open("lineups.json", "w") as file:
        json.dump(lineups, file, indent=4)

def get_point_data():
    points = {"points": {}}

    with open("incidents.json") as file:
        incidents = json.load(file)

    with open("lineups.json") as file:
        lineups = json.load(file)



def get_transfer_data():
    pass

#get lineups so you can count points
#find a way to fetch transfers and disable players not playing anymore

# get_teams_data()
# get_match_data()
get_incident_data()
# get_player_data()
# get_lineup_data()
# get_point_data()
# get_transfer_data()