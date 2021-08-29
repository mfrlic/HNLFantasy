from flask import Flask
import json

app = Flask(__name__)

with open("players.json") as file:
    players = json.load(file)

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
                ''' + players + '''
            </body>
        </html>
    '''

if __name__ == "__main__":
    app.run(debug=True)