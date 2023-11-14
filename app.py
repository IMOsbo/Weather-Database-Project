from flask import Flask, request, render_template
from sqlalchemy import create_engine
import mysql.connector
import pandas as pd


app = Flask(__name__)

conn = mysql.connector.connect(user='root', database='weather', password="1234")

USER="root"
DATABASE="weather"
PW="1234"
pandas_conn = create_engine(f"mysql+mysqlconnector://{USER}:{PW}@127.0.0.1/{DATABASE}")
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

@app.route("/station_query", methods=["POST"])
def showDashboard():
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
#     query = f"""select station, valid, tmpf, relh, sped from asosdata where station = (select station from (select min(station) as station, min(distance) from (select station, lat as Latitude, lat as Longitude,
# (3959 * acos( cos( radians({latitude}) ) * cos( radians( lat) ) * cos( radians({longitude}) - radians(lon) ) + sin( radians({latitude}) ) * sin( radians(lat) ) )) as distance
# from asosmetadata) as test) as thisisamess);"""
    query = f"""select asosdata.valid, asosdata.station, tmpf, relh, sped, lat, lon, elevation from asosdata join asosmetadata on asosdata.station=asosmetadata.station where asosdata.station = (select station from (select min(station) as station, min(distance) from (select station, lat as Latitude, lat as Longitude,
(3959 * acos( cos( radians(35.849) ) * cos( radians( lat) ) * cos( radians(-86.368) - radians(lon) ) + sin( radians(35.849) ) * sin( radians(lat) ) )) as distance
from asosmetadata) as test) as thisisamess);
"""
    with pandas_conn.connect() as connection, connection.begin():  
        data = pd.read_sql(query, connection)
        print(data)
    return render_template("dashboardQuery.html", results = data)

@app.route("/map_query", methods=["POST"])
def showMapQuery():
    mapcursor = conn.cursor()
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    distance = float(request.form["distance"])

    query = f"""with testTable as (select nwsli, high_F as `temp`, Latitude1 as Latitude, Longitude1 as Longitude,
            (3959 * acos( cos( radians({latitude}) ) * cos( radians( Latitude1 ) ) * cos( radians({longitude}) - radians(Longitude1) ) + sin( radians({latitude}) ) * sin( radians(Latitude1) ) )) as distance
            from coopdata join coopmetadata on coopdata.nwsli = coopmetadata.ID where date="2023-10-01")  select * from testTable where distance < {distance} and temp is not null;"""
    with pandas_conn.connect() as connection, connection.begin():  
        data = pd.read_sql(query, connection)
        data = data
        # print(data)
# cursor.execute(f"select id, `Elevation [m]` from coopmetadata where `Elevation [m]` > {elevation} order by `Elevation [m]`")
    return render_template("map.html", results = data, centerLat = latitude, centerLong = longitude, radius = distance)

# @app.route("/station_query", methods=["POST"])
# def stationQuery():


if __name__ == "__main__":
    app.run(debug=True)

