from flask import Flask, render_template
import json

app = Flask(__name__)

with open("web/data.json") as file:
    data = json.load(file)["data"]

# table = "<table class='table'><thead><td></td><td>Ime</td><td>Pozicija</td><td>Klub</td><td>Država</td><td>Bodovi</td></thead>"

# for player in data:
#     table += "<tr>" + "<td>" + '<img src="web/img/players/' + str(player["id"]) + '.png">' + "</td>" + "<td>" + player["shortName"] + "</td>" + "<td>" + ("Vratar" if player["position"] == "G" else "Branič" if player["position"] == "D" else "Vezni" if player["position"] == "M" else "Napadač" if player["position"] == "F" else "Nepoznato") + "</td>"+ "<td>" + '<img src="web/img/clubs/' + (str(player["club"]).lower() if player["club"] != "\u0160ibenik" else "sibenik") + '.png">' + "</td>" + '<td><img src="web/img/flags/' + player["country"].lower() + '.svg">' + "</td>" + "<td>" + str(player["points"]) + "</td>" + "</tr>"

# table += "</table>"

@app.route('/stats')
def stats():
    return render_template("stats.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)