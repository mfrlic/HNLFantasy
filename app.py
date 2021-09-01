from flask import Flask
import json

app = Flask(__name__)

with open("data.json") as file:
    data = json.load(file)["data"]

table = "<table><thead><td>Ime</td><td>Pozicija</td><td>Klub</td><td>Država</td><td>Bodovi</td></thead>"

for player in data:
    table += "<tr>" + "<td>" + player["name"] + "</td>" + "<td>" + player["position"] + "</td>"+ "<td>" + player["club"] + "</td>"+ "<td><img src='web/img/flags/" + player["country"].lower() + ".png'>" + "</td>" + "<td>" + str(player["points"]) + "</td>" + "</tr>"

table += "</table>"

@app.route('/')
def hello():
    return '''
        <html>
            <head>
                <title>HNL Fantasy Liga</title>

                <link href="web/vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet">
                <link href="web/vendor/boxicons/css/boxicons.min.css" rel="stylesheet">
                <link href="web/vendor/aos/aos.css" rel="stylesheet">
                <link href="web/css/style.css" rel="stylesheet">

                <script src="web/vendor/jquery/jquery.min.js"></script>
                <script src='web/vendor/bootstrap/js/bootstrap.min.js'></script>
                <script src="web/vendor/aos/aos.js"></script>
                <script src="web/js/main.js"></script>
            </head>
            <body>
                ''' + table + '''
            </body>
        </html>
    '''

if __name__ == "__main__":
    app.run(debug=True)