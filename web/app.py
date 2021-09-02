from flask import Flask, render_template
import json

app = Flask(__name__)

with open("web/data.json") as file:
    data = json.load(file)["data"]

@app.route('/stats')
def stats():
    return render_template("stats.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)