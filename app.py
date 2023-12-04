from flask import Flask, request, render_template
from sqlalchemy import create_engine, text
import mysql.connector
import pandas as pd

with open("config.txt", "r") as file:
    USER = file.readline().rstrip()
    PW = file.readline().rstrip() 
    DATABASE = file.readline().rstrip()

app = Flask(__name__)

conn = mysql.connector.connect(user='root', database='weather', password="1234")

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

with pandas_conn.connect() as distance:
    distance.execute(text("DROP FUNCTION IF EXISTS distance"))
    distance.execute(text(distanceFunction))
    distance.commit()

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

    ## Adding for col
@app.route("/coopdatasample")
def coopda():
    return render_template("coppmetadatasample.html")

@app.route("/asoscolumn")
def asoscol():
    return render_template("asos_col.html")

@app.route("/coopcolumn")
def coopcol():
    return render_template("coop_col.html")
## Adding column information end


@app.route("/insert")
def insert():
    return render_template("insert.html")

# this handles all of our query paths
@app.route("/query_elevation", methods=["POST"])
def showElevation():
    cursor = conn.cursor()
    elevation = request.form["elevation"]
    # https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-execute.html
    # cursor.execute("""select id, `Elevation [m]` from coopmetadata where `Elevation [m]` > %(elevation)s order by `Elevation [m]`""", params={"elevation": elevation})
    cursor.execute("""select * from ((select id as Station, `Elevation [m]` as Elevation, "COOP" as Network from coopmetadata) union all (select station as Station, elevation as Elevation, "ASOS" as Network from asosmetadata)) as t order by abs(Elevation - %(elevation)s)""", params={"elevation": elevation})
    return render_template("queryResult.html", results = cursor)


@app.route("/query_longitude", methods=["POST"])
def showLongitude():
    cursor = conn.cursor()
    longitude = request.form["longitude"]
    cursor.execute("""select * from ((select id as Station, Longitude1 as Longitude, "COOP" as Network from coopmetadata) union all (select station as Station, lon as Longitude, "ASOS" as Network from asosmetadata)) as t order by abs(Longitude - %(longitude)s)""", params={"longitude": longitude})
    return render_template("longitudeQueryResult.html", results = cursor)


@app.route("/query_latitude", methods=["POST"])
def showLatitude():
    cursor = conn.cursor(buffered=True)
    latitude = request.form["latitude"]
    cursor.execute("""select * from ((select id as Station, Latitude1 as Latitude, "COOP" as Network from coopmetadata) union all (select station as Station, lat as Latitude, "ASOS" as Network from asosmetadata)) as t order by abs(Latitude - %(latitude)s)""", params={"latitude": latitude})
    return render_template("latitudeQueryResult.html", results = cursor)
    


@app.route("/query_distance", methods=["POST"])
def showDistance():
    cursor = conn.cursor(buffered=True)
    latitude1 = request.form["latitude1"]
    longitude1 = request.form["longitude1"]
    try:
        cursor.execute("""select * from ((select id as Station, Longitude1 as Longitude, Latitude1 as Latitude, "COOP" as Network, truncate(ST_Distance_Sphere(point(Longitude1, Latitude1),point(%(longitude1)s,%(latitude1)s))/1000,3) as Distance from coopmetadata) union all (select station as Station, lon as Longitude, lat as Latitude, "ASOS" as Network, truncate(ST_Distance_Sphere(point(lon, lat),point(%(longitude1)s,%(latitude1)s))/1000,3) as Distance from asosmetadata)) as t order by Distance""", params={"latitude1": latitude1, "longitude1" : longitude1})
        return render_template("distanceQueryResult.html", results = cursor)
    except Exception as e:
        return("Please enter acceptable longitude and latitude values. Longitude may include values from -180 to 180, while latitude may include values from -90 to 90.")
    #return render_template("distanceQueryResult.html", results = cursor)

@app.route("/station_query", methods=["POST"])
def showDashboard():
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    
    with pandas_conn.connect() as connection, connection.begin():  
        network = pd.read_sql(closestStation(latitude, longitude), connection, params={"a": latitude, "o": longitude})
    print(network)
    if network["Network"][0] == "ASOS":
        # these queries are relying on database values, so not 
        # vulnerable to SQL injection (hypothetically)
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
    latitude = float(request.form["latitude"])
    longitude = float(request.form["longitude"])
    distance = float(request.form["distance"])
    date = str(request.form["date"]) + " 00:00:00"
    print(latitude)
    print(longitude)
    print(distance)
    print(date)
    query = text("""
    with testTable as (select nwsli, high_F as `temp`, Latitude1 as Latitude, Longitude1 as Longitude,
    distance(:a, :o, Latitude1, Longitude1) as distance
    from coopdata join coopmetadata on coopdata.nwsli = coopmetadata.ID where date=:t)  
    select * from testTable where distance < :d and temp is not null;
    """)
    print(query)
    with pandas_conn.connect() as connection, connection.begin():  
        data = pd.read_sql(query, connection, params={"a": latitude, "o": longitude, "t": date, "d": distance})
    return render_template("map.html", results = data, centerLat = latitude, centerLong = longitude, radius = distance, date=date)

if __name__ == "__main__":
    app.run(debug=True)

