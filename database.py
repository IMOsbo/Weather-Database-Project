# coding: utf-8
import mysql.connector
from sqlalchemy import create_engine, text, exc
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


# our datatypes get kinda weird with the csvs, so clean them up!
def convertDataTypes(data):
    for col in list(data):
        data[col] = data[col].replace("M", -500)
        data[col] = data[col].replace("T", 0.0001)
        try:
            data[col] = pd.to_numeric(data[col])
        except:
            try:
                data[col] = pd.to_datetime(data[col])
            except:
                pass

with open("config.txt", "r") as file:
    USER = file.readline().rstrip()
    PW = file.readline().rstrip() 
    DATABASE = file.readline().rstrip()
# create our database connection
conn = create_engine(f"mysql+mysqlconnector://{USER}:{PW}@127.0.0.1/")

try:
    with conn.connect() as con: 
        con.execute(text(f"use {DATABASE}"))
        confirm = input(f"Database {DATABASE} already exists - override? (Y/N): ")
        while confirm != "Y" and confirm != "N":
            confirm = input("\tPlease enter Y or N: ")
        if confirm.lower() == "y":
            con.execute(text(f"drop database {DATABASE}"))
            con.execute(text(f"create database {DATABASE}"))
            print(f"Successfully dropped and created {DATABASE}")
        else:
            print("Aborting - no database created.")
            quit()
except exc.ProgrammingError as e:
    print(f"Database {DATABASE} does not exist; will be created.")
    with conn.connect() as con:
        con.execute(text(f"create database {DATABASE}"))

# now that we have connected, we can create a new connection
conn = create_engine(f"mysql+mysqlconnector://{USER}:{PW}@127.0.0.1/{DATABASE}")


# read the coop data
coopData = pd.read_csv("coopData.csv")
convertDataTypes(coopData)
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dropna.html
coopData = coopData.dropna(subset=["high_F", "low_F", "time"])


# read our Coop metadata
coopMetadata = pd.read_html("https://mesonet.agron.iastate.edu/sites/networks.php?network=TN_COOP&format=html&nohtml=on")
convertDataTypes(coopMetadata[0])

# read our asos data
asosData = pd.read_csv("filteredasosdata.csv")
convertDataTypes(asosData)

# do some time filtering on our asosdata
asosData["time"] = asosData["valid"].astype("str").str.slice(11,13)
asosData["valid"] = asosData["valid"].astype("str").str.slice(0,11)
asosData = asosData[asosData["time"] == "12"]
asosData = asosData.drop_duplicates(subset=["station", "valid"])

# read our metadata
asosMetadata = pd.read_csv("asosMetadata.csv").drop("wxcodes", axis=1)
convertDataTypes(asosMetadata)
asosMetadata = asosMetadata.drop_duplicates(subset=["station"])

try:
    coopData.to_sql(name='coopdata', con=conn)
    print(f"Inserted {len(coopData)} rows of COOP data!")
except:
    print("Could not insert COOP data - maybe you've already done it?")

try:
    coopMetadata[0].to_sql(name='coopmetadata', con=conn)
    print(f"Inserted {len(coopMetadata[0])} rows of COOP metadata!")
except:
    print("Could not insert COOP metadata - maybe you've already done it?")

try:
    asosData.to_sql(name='asosdata', con=conn)
    print(f"Inserted {len(asosData)} rows of ASOS data!")
except:
    print("Could not insert ASOS data - maybe you've already done it?")

try:
    asosMetadata.to_sql(name='asosmetadata', con=conn)
    print(f"Inserted {len(asosMetadata)} rows of ASOS metadata!")
except:
    print("Could not insert ASOS metadata - maybe you've already done it?")

with open("constraints.sql") as file, conn.connect() as con:
    for line in file:
        line = line.rstrip();
        print(f"Applying constraint {line} ", end="")
        try:
            con.execute(text(line))
            print("✅")
        except Exception as e:
            print("❌")
            print(e)

