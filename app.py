from flask import Flask, request, render_template
from sqlalchemy import create_engine, text
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

# https://dev.mysql.com/doc/refman/5.7/en/create-procedure.html
# https://learn.microsoft.com/en-us/sql/relational-databases/user-defined-functions/create-user-defined-functions-database-engine
distanceFunction = """
CREATE FUNCTION distance (startingLat float, startingLong float, latitude float, longitude float)
RETURNS float DETERMINISTIC
RETURN (3959 * acos( cos( radians(startingLat) ) * cos( radians(latitude) ) * cos( radians(startingLong) - radians(longitude)) + sin(radians(startingLat) ) * sin(radians(latitude) )));
"""

def closestStation(lat, lon):
    return text("""
    select * from
        ((select ID as Station, distance(:a, :o, Latitude1, Longitude1) as Distance, "COOP" as Network from coopmetadata)
        union all (select Station, distance(:a, :o, lat, lon) as Distance, "ASOS" as Network  from asosmetadata)) as metadata
    order by Distance limit 1;
    """)

with pandas_conn.connect() as conn:
    conn.execute(text("DROP FUNCTION IF EXISTS distance"))
    conn.execute(text(distanceFunction))
    conn.commit()

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


@app.route("/insert")
def insert():
    return render_template("insert.html")

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
    
    with pandas_conn.connect() as connection, connection.begin():  
        network = pd.read_sql(closestStation(latitude, longitude), connection, params={"a": latitude, "o": longitude})
    print(network)
    if network["Network"][0] == "ASOS":
        query = f"""
        select asosdata.valid, asosdata.station, tmpf, relh, sped, lat, lon, elevation from 
        asosdata join asosmetadata on asosdata.station=asosmetadata.station 
        where asosdata.station = "{network["Station"][0]}"
        """
        with pandas_conn.connect() as connection, connection.begin():  
            data = pd.read_sql(query, connection)

        return render_template("dashboardQuery.html", results = data, network=network["Network"][0])
    else:
        query = f"""
        select nwsli as station, high_F, low_F, `date`, Latitude1 as lat, Longitude1 as lon, `Elevation [m]` as elevation from coopdata join coopmetadata on coopdata.nwsli=coopmetadata.id where coopdata.nwsli="{network["Station"][0]}";
        """

        with pandas_conn.connect() as connection, connection.begin():  
            data = pd.read_sql(query, connection)
        return render_template("dashboardQueryCOOP.html", results = data, network=network["Network"][0])

@app.route("/map_query", methods=["POST"])
def showMapQuery():
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    distance = float(request.form["distance"])
    date = str(request.form["date"])
    print(date)
    query = f"""
    with testTable as (select nwsli, high_F as `temp`, Latitude1 as Latitude, Longitude1 as Longitude,
    distance({latitude}, {longitude}, Latitude1, Longitude1) as distance
    from coopdata join coopmetadata on coopdata.nwsli = coopmetadata.ID where date="{date}")  
    select * from testTable where distance < {distance} and temp is not null;
    """
    print(query)
    with pandas_conn.connect() as connection, connection.begin():  
        data = pd.read_sql(query, connection)
    return render_template("map.html", results = data, centerLat = latitude, centerLong = longitude, radius = distance, date=date)

# @app.route("/insert_query", methods=["POST"])
# def insertQuery():
#     fileName = request.form["file"]
#     network = request.form["network"]
#     if network == "ASOS":
#         asosData = pd.read_csv("filteredasosdata.csv")
#         convertDataTypes(asosData)
#
#         asosData["time"] = asosData["valid"].str.slice(11,13)
#         asosData["valid"] = asosData["valid"].str.slice(0,11)
#         asosData = asosData[asosData["time"] == "12"]
#         asosData = asosData.drop_duplicates(subset=["station", "valid"])
#         try:
#             asosData.to_sql(name='asosdata', con=conn, if_exists="append")
#         except:
#             result = "Could not add new ASOS data."
#     else:
#         coopData = pd.read_csv("coopData.csv")
#         coopData.to_sql(name='coopdata', con=pandas_conn, if_exists="append")
if __name__ == "__main__":
    app.run(debug=True)

