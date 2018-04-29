from flask import Flask, render_template, jsonify, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

mongo = PyMongo(app)


@app.route("/")
def index():
    listings = mongo.db.marsNews.find()
    return render_template("index.html", listings=listings)

@app.route("/clear")
def clear():
    result = mongo.db.marsNews.delete_many({})
    return redirect("http://127.0.0.1:5000/", code=302)

@app.route("/scrape")
def scrape():
    # listings = mongo.db.marsNews
    listings_data = scrape_mars.scrape() 
    return redirect("http://127.0.0.1:5000/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
