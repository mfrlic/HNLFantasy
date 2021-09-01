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
            flag = False
            if(match["status"]["type"] == "finished"):
                for matchid in matches["matches"]:
                    if matchid["id"] == match["id"]:
                        flag = True
                if not flag:
                    matches["matches"].append({ "homeTeam": match["homeTeam"]["nameCode"], 
                                                "homeScore": match["homeScore"]["display"], 
                                                "awayTeam": match["awayTeam"]["nameCode"], 
                                                "awayScore": match["awayScore"]["display"], 
                                                "startTimestamp": match["startTimestamp"], 
                                                "winnerCode": match["winnerCode"], 
                                                "id": match["id"] })

    with open("matches.json", "w") as file:
        json.dump(matches, file, indent=4)

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

def get_point_data():
    points = {"points": {}}

    with open("teams.json") as file:
        teams = json.load(file)

    with open("players.json") as file:
        players = json.load(file)

    with open("matches.json") as file:
        matches = json.load(file)

    incidents = { "incidents" : {} }

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
                incidents["incidents"][str(match["id"])].append({ "goalscorer": incident["player"]["id"], "assist": assist, "time": incident["time"], "isHome": incident["isHome"], "incidentClass": incident["incidentClass"], "incidentType": "goal" })
            elif incident["incidentType"] == "inGamePenalty":
                if incident["description"] == "Goalkeeper save": 
                    saved = True
                else:
                    saved = False
                incidents["incidents"][str(match["id"])].append({ "player": incident["player"]["id"], "saved": saved, "time": incident["time"], "isHome": incident["isHome"], "incidentType": "penaltyMissed" })


    lineups = { "lineups": {} }

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

    for team in teams["teams"]:
        for player in players["players"][str(team["id"])]:
            points["points"][player["id"]] = []
            for match in matches["matches"]:
                for appearance in lineups["lineups"][str(match["id"])]["home"]:
                    goals = 0
                    ownGoals = 0
                    assists = 0
                    yellow = 0
                    red = 0
                    goalsConceded = 0
                    saves = 0
                    cleanSheet = False
                    pointsTotal = 0
                    penaltyMissed = 0
                    penaltySaved = 0

                    if player["id"] == appearance["id"]:
                        for incident in incidents["incidents"][str(match["id"])]:
                            if incident["incidentType"] == "goal":
                                if incident["goalscorer"] == player["id"]:
                                    if incident["incidentClass"] == "ownGoal":
                                        ownGoals += 1
                                    else:
                                        goals += 1
                                elif incident["assist"] == player["id"]:
                                    assists += 1
                                elif not incident["isHome"] or incident["isHome"] and incident["incidentClass"] == "ownGoal":
                                    if not appearance["substitute"]:
                                        if appearance["minutesPlayed"] >= incident["time"]:
                                            goalsConceded += 1
                                    else:
                                        if (90 - appearance["minutesPlayed"]) >= incident["time"]:
                                            goalsConceded += 1
                            elif incident["incidentType"] == "card":
                                if incident["player"] == player["id"] and incident["card"] == "yellow":
                                    yellow += 1
                                elif incident["player"] == player["id"] and incident["card"] == "red":
                                    red += 1
                            elif incident["incidentType"] == "penaltyMissed" and incident["saved"]:
                                if incident["isHome"] and player["id"] == incident["player"]:
                                    penaltyMissed += 1
                                elif not incident["isHome"] and player["position"] == "G" and appearance["minutesPlayed"] >= incident["time"]:
                                    penaltySaved += 1

                        if appearance["minutesPlayed"] >= 60:
                            minutesPlayedPoints = 2
                        elif 0 < appearance["minutesPlayed"] < 60:
                            minutesPlayedPoints = 1
                        else:
                            minutesPlayedPoints = 0

                        assistsPoints = assists * 3

                        if yellow == 0 and red == 0:
                            cardPoints = 0
                        elif yellow == 1 and red == 0:
                            cardPoints = -1
                        elif red == 1:
                            cardPoints = -3
                        ownGoalsPoints = ownGoals * -2
                        penaltyMissedPoints = penaltyMissed * -2

                        if player["position"] == "G" or player["position"] == "D" or player["position"] == "M":
                            if appearance["minutesPlayed"] >= 60 and goalsConceded == 0:
                                cleanSheet = True
                                if player["position"] == "G" or player["position"] == "D":
                                    cleanSheetPoints = 4
                                elif player["position"] == "M":
                                    cleanSheetPoints = 1
                            else:
                                cleanSheetPoints = 0
                        
                        if player["position"] == "G" or player["position"] == "D":
                            goalsPoints = goals * 6

                            if 2 > goalsConceded >= 0:
                                goalsConcededPoints = 0
                            elif 4 > goalsConceded >= 2:
                                goalsConcededPoints = -1
                            elif 6 > goalsConceded >= 4:
                                goalsConcededPoints = -2
                            elif 8 > goalsConceded >= 6:
                                goalsConcededPoints = -3
                            elif 10 > goalsConceded >= 8:
                                goalsConcededPoints = -4
                            elif 12 > goalsConceded >= 10:
                                goalsConcededPoints = -5
                            elif 14 > goalsConceded >= 12:
                                goalsConcededPoints = -6
                            elif 16 > goalsConceded >= 14:
                                goalsConcededPoints = -7
                            elif 18 > goalsConceded >= 16:
                                goalsConcededPoints = -8
                            elif 20 > goalsConceded >= 18:
                                goalsConcededPoints = -9
                            elif 22 > goalsConceded >= 20:
                                goalsConcededPoints = -10

                        if player["position"] == "G":
                            try:
                                saves = appearance["saves"]
                            except:
                                saves = 0
                            if 3 > saves >= 0:
                                savesPoints = 0
                            elif 6 > saves >= 3 :
                                savesPoints = 1
                            elif 9 > saves >= 6:
                                savesPoints = 2
                            elif 12 > saves >= 9:
                                savesPoints = 3
                            elif 15 > saves >= 12:
                                savesPoints = 4
                            elif 18 > saves >= 15:
                                savesPoints = 5
                            elif 21 > saves >= 18:
                                savesPoints = 6
                            elif 24 > saves >= 21:
                                savesPoints = 7
                            elif 27 > saves >= 24:
                                savesPoints = 8
                            elif 30 > saves >= 27:
                                savesPoints = 9
                            elif 33 > saves >= 30:
                                savesPoints = 10
                            elif 36 > saves >= 33:
                                savesPoints = 11
                            elif 39 > saves >= 36:
                                savesPoints = 12
                            elif 42 > saves >= 39:
                                savesPoints = 13
                            elif 45 > saves >= 42:
                                savesPoints = 14
                            elif 48 > saves >= 45:
                                savesPoints = 15
                            penaltySavedPoints = penaltySaved * 5
                            pointsTotal = minutesPlayedPoints + cleanSheetPoints + goalsPoints + assistsPoints + savesPoints + goalsConcededPoints + cardPoints + ownGoalsPoints + penaltyMissedPoints + penaltySavedPoints
                            points["points"][player["id"]].append({ "id": match["id"], "pointsTotal": pointsTotal, "minutesPlayed": appearance["minutesPlayed"], "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "goalsConceded": goalsConceded, "goalsConcededPoints": goalsConcededPoints, "cleanSheet": cleanSheet, "cleanSheetPoints": cleanSheetPoints, "saves": saves, "savesPoints": savesPoints, "penaltiesSaved": penaltySaved, "penaltiesSavedPoints": penaltySavedPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellow, "redCard": red, "cardPoints": cardPoints })
                        elif player["position"] == "D":
                            pointsTotal = minutesPlayedPoints + cleanSheetPoints + goalsPoints + assistsPoints + goalsConcededPoints + cardPoints + ownGoalsPoints + penaltyMissedPoints
                            points["points"][player["id"]].append({ "id": match["id"], "pointsTotal": pointsTotal, "minutesPlayed": appearance["minutesPlayed"], "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "goalsConceded": goalsConceded, "goalsConcededPoints": goalsConcededPoints, "cleanSheet": cleanSheet, "cleanSheetPoints": cleanSheetPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellow, "redCard": red, "cardPoints": cardPoints })
                        elif player["position"] == "M":
                            goalsPoints = goals * 5
                            pointsTotal = minutesPlayedPoints + cleanSheetPoints + goalsPoints + assistsPoints + cardPoints + ownGoalsPoints + penaltyMissedPoints
                            points["points"][player["id"]].append({ "id": match["id"], "pointsTotal": pointsTotal, "minutesPlayed": appearance["minutesPlayed"], "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "cleanSheet": cleanSheet, "cleanSheetPoints": cleanSheetPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellow, "redCard": red, "cardPoints": cardPoints })
                        elif player["position"] == "F":
                            goalsPoints = goals * 4
                            pointsTotal = minutesPlayedPoints + goalsPoints + assistsPoints + cardPoints + ownGoalsPoints + penaltyMissedPoints
                            points["points"][player["id"]].append({ "id": match["id"], "pointsTotal": pointsTotal, "minutesPlayed": appearance["minutesPlayed"], "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellow, "redCard": red, "cardPoints": cardPoints })


                for appearance in lineups["lineups"][str(match["id"])]["away"]:
                    goals = 0
                    ownGoals = 0
                    assists = 0
                    yellow = 0
                    red = 0
                    goalsConceded = 0
                    saves = 0
                    cleanSheet = False
                    pointsTotal = 0
                    penaltyMissed = 0
                    penaltySaved = 0

                    if player["id"] == appearance["id"]:
                        for incident in incidents["incidents"][str(match["id"])]:
                            if incident["incidentType"] == "goal":
                                if incident["goalscorer"] == player["id"]:
                                    if incident["incidentClass"] == "ownGoal":
                                        ownGoals += 1
                                    else:
                                        goals += 1
                                elif incident["assist"] == player["id"]:
                                    assists += 1
                                elif incident["isHome"] or not incident["isHome"] and incident["incidentClass"] == "ownGoal":
                                    if not appearance["substitute"]:
                                        if appearance["minutesPlayed"] >= incident["time"]:
                                            goalsConceded += 1
                                    else:
                                        if (90 - appearance["minutesPlayed"]) >= incident["time"]:
                                            goalsConceded += 1
                            elif incident["incidentType"] == "card":
                                if incident["player"] == player["id"] and incident["card"] == "yellow":
                                    yellow += 1
                                elif incident["player"] == player["id"] and incident["card"] == "red":
                                    red += 1
                            elif incident["incidentType"] == "penaltyMissed" and incident["saved"]:
                                if not incident["isHome"] and player["id"] == incident["player"]:
                                    penaltyMissed += 1
                                elif incident["isHome"] and player["position"] == "G" and appearance["minutesPlayed"] >= incident["time"]:
                                    penaltySaved += 1

                        if appearance["minutesPlayed"] >= 60:
                            minutesPlayedPoints = 2
                        elif 0 < appearance["minutesPlayed"] < 60:
                            minutesPlayedPoints = 1
                        else:
                            minutesPlayedPoints = 0

                        assistsPoints = assists * 3

                        if yellow == 0 and red == 0:
                            cardPoints = 0
                        elif yellow == 1 and red == 0:
                            cardPoints = -1
                        elif red == 1:
                            cardPoints = -3
                        ownGoalsPoints = ownGoals * -2
                        penaltyMissedPoints = penaltyMissed * -2

                        if appearance["minutesPlayed"] >= 60 and goalsConceded == 0:
                            cleanSheet = True
                            if player["position"] == "G" or player["position"] == "D":
                                cleanSheetPoints = 4
                            elif player["position"] == "M":
                                cleanSheetPoints = 1
                        else:
                            cleanSheetPoints = 0
                        
                        if player["position"] == "G" or player["position"] == "D":
                            goalsPoints = goals * 6

                            if 2 > goalsConceded >= 0:
                                goalsConcededPoints = 0
                            elif 4 > goalsConceded >= 2:
                                goalsConcededPoints = -1
                            elif 6 > goalsConceded >= 4:
                                goalsConcededPoints = -2
                            elif 8 > goalsConceded >= 6:
                                goalsConcededPoints = -3
                            elif 10 > goalsConceded >= 8:
                                goalsConcededPoints = -4
                            elif 12 > goalsConceded >= 10:
                                goalsConcededPoints = -5
                            elif 14 > goalsConceded >= 12:
                                goalsConcededPoints = -6
                            elif 16 > goalsConceded >= 14:
                                goalsConcededPoints = -7
                            elif 18 > goalsConceded >= 16:
                                goalsConcededPoints = -8
                            elif 20 > goalsConceded >= 18:
                                goalsConcededPoints = -9
                            elif 22 > goalsConceded >= 20:
                                goalsConcededPoints = -10

                        if player["position"] == "G":
                            try:
                                saves = appearance["saves"]
                            except:
                                saves = 0
                            if 3 > saves >= 0:
                                savesPoints = 0
                            elif 6 > saves >= 3 :
                                savesPoints = 1
                            elif 9 > saves >= 6:
                                savesPoints = 2
                            elif 12 > saves >= 9:
                                savesPoints = 3
                            elif 15 > saves >= 12:
                                savesPoints = 4
                            elif 18 > saves >= 15:
                                savesPoints = 5
                            elif 21 > saves >= 18:
                                savesPoints = 6
                            elif 24 > saves >= 21:
                                savesPoints = 7
                            elif 27 > saves >= 24:
                                savesPoints = 8
                            elif 30 > saves >= 27:
                                savesPoints = 9
                            elif 33 > saves >= 30:
                                savesPoints = 10
                            elif 36 > saves >= 33:
                                savesPoints = 11
                            elif 39 > saves >= 36:
                                savesPoints = 12
                            elif 42 > saves >= 39:
                                savesPoints = 13
                            elif 45 > saves >= 42:
                                savesPoints = 14
                            elif 48 > saves >= 45:
                                savesPoints = 15
                            penaltySavedPoints = penaltySaved * 5
                            pointsTotal = minutesPlayedPoints + cleanSheetPoints + goalsPoints + assistsPoints + savesPoints + goalsConcededPoints + cardPoints + ownGoalsPoints + penaltyMissedPoints + penaltySavedPoints
                            points["points"][player["id"]].append ({ "id": match["id"], "pointsTotal": pointsTotal, "minutesPlayed": appearance["minutesPlayed"], "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "goalsConceded": goalsConceded, "goalsConcededPoints": goalsConcededPoints, "cleanSheet": cleanSheet, "cleanSheetPoints": cleanSheetPoints, "saves": saves, "savesPoints": savesPoints, "penaltiesSaved": penaltySaved, "penaltiesSavedPoints": penaltySavedPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellow, "redCard": red, "cardPoints": cardPoints })
                        elif player["position"] == "D":
                            pointsTotal = minutesPlayedPoints + cleanSheetPoints + goalsPoints + assistsPoints + goalsConcededPoints + cardPoints + ownGoalsPoints + penaltyMissedPoints
                            points["points"][player["id"]].append({ "id": match["id"], "pointsTotal": pointsTotal, "minutesPlayed": appearance["minutesPlayed"], "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "goalsConceded": goalsConceded, "goalsConcededPoints": goalsConcededPoints, "cleanSheet": cleanSheet, "cleanSheetPoints": cleanSheetPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellow, "redCard": red, "cardPoints": cardPoints })
                        elif player["position"] == "M":
                            goalsPoints = goals * 5
                            pointsTotal = minutesPlayedPoints + cleanSheetPoints + goalsPoints + assistsPoints + cardPoints + ownGoalsPoints + penaltyMissedPoints
                            points["points"][player["id"]].append({ "id": match["id"], "pointsTotal": pointsTotal, "minutesPlayed": appearance["minutesPlayed"], "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "cleanSheet": cleanSheet, "cleanSheetPoints": cleanSheetPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellow, "redCard": red, "cardPoints": cardPoints })
                        elif player["position"] == "F":
                            goalsPoints = goals * 4
                            pointsTotal = minutesPlayedPoints + goalsPoints + assistsPoints + cardPoints + ownGoalsPoints + penaltyMissedPoints
                            points["points"][player["id"]].append({ "id": match["id"], "pointsTotal": pointsTotal, "minutesPlayed": appearance["minutesPlayed"], "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellow, "redCard": red, "cardPoints": cardPoints })


    with open("points.json", "w") as file:
        json.dump(points, file, indent=4)

def get_transfer_data():
    pass

def get_final_data():
    with open("teams.json") as file:
        teams = json.load(file)

    with open("players.json") as file:
        players = json.load(file)

    with open("matches.json") as file:
        matches = json.load(file)

    with open("points.json") as file:
        points = json.load(file)

    dataFinal = {"data": []}

    for team in teams["teams"]:
        for player in players["players"][str(team["id"])]:
            totalPoints = 0
            playerMatches = []
            name = player["name"]
            shortName = player["shortName"]
            position = player["position"]
            country = player["country"]
            club = team["name"]
            for data in points["points"][str(player["id"])]:
                matchid = data["id"]
                pointsTotal = data["pointsTotal"]
                totalPoints += pointsTotal
                minutesPlayed = data["minutesPlayed"]
                minutesPlayedPoints = data["minutesPlayedPoints"]
                goals = data["goals"]
                goalsPoints = data["goalsPoints"]
                assists = data["assists"]
                assistsPoints = data["assistsPoints"]
                ownGoals = data["ownGoals"]
                ownGoalsPoints = data["ownGoalsPoints"]
                penaltyMissed = data["penaltiesMissed"]
                penaltyMissedPoints = data["penaltiesMissedPoints"]
                yellowCard = data["yellowCard"]
                redCard = data["redCard"]
                cardPoints = data["cardPoints"]
                if position == "G": 
                    goalsConceded = data["goalsConceded"]
                    goalsConcededPoints = data["goalsConcededPoints"]
                    cleanSheet = data["cleanSheet"]
                    cleanSheetPoints = data["cleanSheetPoints"]
                    saves = data["saves"]
                    savesPoints = data["savesPoints"]
                    penaltySaved = data["penaltiesSaved"]
                    penaltySavedPoints = data["penaltiesSavedPoints"]
                elif position == "D":
                    goalsConceded = data["goalsConceded"]
                    goalsConcededPoints = data["goalsConcededPoints"]
                    cleanSheet = data["cleanSheet"]
                    cleanSheetPoints = data["cleanSheetPoints"]
                elif position == "M":
                    cleanSheet = data["cleanSheet"]
                    cleanSheetPoints = data["cleanSheetPoints"]

                for match in matches["matches"]:
                    if match["id"] == matchid:
                        homeTeam = match["homeTeam"]
                        homeScore = match["homeScore"]
                        awayTeam = match["awayTeam"]
                        awayScore = match["awayScore"]
                        winnerCode = match["winnerCode"]
                        startTimestamp = match["startTimestamp"]
                if position == "G":
                    playerMatches.append({ "homeTeam": homeTeam, "homeScore": homeScore, "awayTeam": awayTeam, "awayScore": awayScore, "winnerCode": winnerCode, "startTimestamp": startTimestamp, "pointsTotal": pointsTotal, "minutesPlayed": minutesPlayed, "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "goalsConceded": goalsConceded, "goalsConcededPoints": goalsConcededPoints, "cleanSheet": cleanSheet, "cleanSheetPoints": cleanSheetPoints, "saves": saves, "savesPoints": savesPoints, "penaltiesSaved": penaltySaved, "penaltiesSavedPoints": penaltySavedPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellowCard, "redCard": redCard, "cardPoints": cardPoints })
                elif position == "D":
                    playerMatches.append({ "homeTeam": homeTeam, "homeScore": homeScore, "awayTeam": awayTeam, "awayScore": awayScore, "winnerCode": winnerCode, "startTimestamp": startTimestamp, "pointsTotal": pointsTotal, "minutesPlayed": minutesPlayed, "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "goalsConceded": goalsConceded, "goalsConcededPoints": goalsConcededPoints, "cleanSheet": cleanSheet, "cleanSheetPoints": cleanSheetPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellowCard, "redCard": redCard, "cardPoints": cardPoints })
                elif position == "M":
                    playerMatches.append({ "homeTeam": homeTeam, "homeScore": homeScore, "awayTeam": awayTeam, "awayScore": awayScore, "winnerCode": winnerCode, "startTimestamp": startTimestamp, "pointsTotal": pointsTotal, "minutesPlayed": minutesPlayed, "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "cleanSheet": cleanSheet, "cleanSheetPoints": cleanSheetPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellowCard, "redCard": redCard, "cardPoints": cardPoints })
                elif position == "F":
                    playerMatches.append({ "homeTeam": homeTeam, "homeScore": homeScore, "awayTeam": awayTeam, "awayScore": awayScore, "winnerCode": winnerCode, "startTimestamp": startTimestamp, "pointsTotal": pointsTotal, "minutesPlayed": minutesPlayed, "minutesPlayedPoints": minutesPlayedPoints, "goals": goals, "goalsPoints": goalsPoints, "assists": assists, "assistsPoints": assistsPoints, "ownGoals": ownGoals, "ownGoalsPoints": ownGoalsPoints, "penaltiesMissed": penaltyMissed, "penaltiesMissedPoints": penaltyMissedPoints, "yellowCard": yellowCard, "redCard": redCard, "cardPoints": cardPoints })

            dataFinal["data"].append({ "name": name, "shortName": shortName, "position": position, "club": club, "country": country, "points": totalPoints, "matches": playerMatches })

    with open("data.json", "w") as file:
        json.dump(dataFinal, file, indent=4)

#find a way to fetch transfers and disable players not playing anymore

# get_teams_data()
# get_match_data()
# get_incident_data()
# get_player_data()
# get_lineup_data()
# get_point_data()
# get_transfer_data()
get_final_data()