from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__)

conn = mysql.connector.connect(user='root', database='weather', password="1234")

# Code heavily inspired by this:
#     https://manojahi.medium.com/flask-html-template-with-mysql-2f3b9405d0e2
# Thank you!!


# this handles all of our pages
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("readme.html")

@app.route("/mapQuery")
def mapQuery():
    return render_template("mapQuery.html")

@app.route("/query")
def query():
    return render_template("query.html")

@app.route("/stationQuery")
def stationQuery():
    return render_template("stationQuery.html")

# this handles all of our query paths
@app.route("/query_elevation", methods=["POST"])
def showElevation():
    cursor = conn.cursor()
    elevation = request.form["elevation"]
    cursor.execute(f"select id, `Elevation [m]` from coopmetadata where `Elevation [m]` > {elevation} order by `Elevation [m]`")
    return render_template("queryResult.html", results = cursor)

@app.route("/map_query", methods=["POST"])
def showMapQuery():
    mapcursor = conn.cursor()
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    distance = float(request.form["distance"])
    # query = f"with testTable as (select nwsli, high_F as `temp`, Latitude1 as Latitude, Longitude1 as Longitude, (3959 * acos( cos( radians({latitude}) ) * cos( radians( Latitude1 ) ) * cos( radians({longitude}) - radians(Longitude1) ) + sin( radians({latitude}) ) * sin( radians(Latitude1) ) )) as distance from coopdata join coopmetadata on coopdata.nwsli = coopmetadata.ID where date='2023-10-01')  select * from testTable where distance < 50 and temp is not null;"

    query = """with testTable as (select nwsli, high_F as `temp`, Latitude1 as Latitude, Longitude1 as Longitude,
(3959 * acos( cos( radians(35.849) ) * cos( radians( Latitude1 ) ) * cos( radians(-86.368) - radians(Longitude1) ) + sin( radians(35.849) ) * sin( radians(Latitude1) ) )) as distance
from coopdata join coopmetadata on coopdata.nwsli = coopmetadata.ID where date="2023-10-01")  select * from testTable where distance < 50 and temp is not null;"""
# cursor.execute(f"select id, `Elevation [m]` from coopmetadata where `Elevation [m]` > {elevation} order by `Elevation [m]`")
    mapcursor.execute(query)
    return render_template("map.html", results = mapcursor, centerLat = latitude, centerLong = longitude, radius = distance)

if __name__ == "__main__":
    app.run(debug=True)

