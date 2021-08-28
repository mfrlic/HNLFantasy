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
            incidents["incidents"][str(match["id"])].append(incident)

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

def get_points_data():
    pass

def get_transfer_data():
    pass


# get_teams_data()
# get_match_data()
# get_incident_data()
get_player_data()