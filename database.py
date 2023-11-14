# coding: utf-8
import mysql.connector
from sqlalchemy import create_engine
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


# our datatypes get kinda weird with the csvs, so clean them up!
def convertDataTypes(data):
    data = data.replace("M", -500)
    data = data.replace("T", 0.0001)
    for col in list(data):
        try:
            data[col] = pd.to_numeric(data[col])
        except:
            try:
                data[col] = pd.to_datetime(data[col])
            except:
                pass
#  _____  _   _   ___   _   _  _____  _____    ___  ___ _____  _  _ 
# /  __ \| | | | / _ \ | \ | ||  __ \|  ___|   |  \/  ||  ___|| || |
# | /  \/| |_| |/ /_\ \|  \| || |  \/| |__     | .  . || |__  | || |
# | |    |  _  ||  _  || . ` || | __ |  __|    | |\/| ||  __| | || |
# | \__/\| | | || | | || |\  || |_\ \| |___    | |  | || |___ |_||_|
#  \____/\_| |_/\_| |_/\_| \_/ \____/\____/    \_|  |_/\____/ (_)(_)
USER = "root"
# don't make fun of me :)
PW = "1234"
# run create database weather;
DATABASE = "weather"
# create our database connection
conn = create_engine(f"mysql+mysqlconnector://{USER}:{PW}@127.0.0.1/{DATABASE}")

# read the coop data
coopData = pd.read_csv("coopData.csv")
convertDataTypes(coopData)

# read our Coop metadata
coopMetadata = pd.read_html("https://mesonet.agron.iastate.edu/sites/networks.php?network=TN_COOP&format=html&nohtml=on")
convertDataTypes(coopMetadata[0])

# read our asos data
asosData = pd.read_csv("filteredasosdata.csv")
convertDataTypes(asosData)

asosData["time"] = asosData["valid"].str.slice(11,13)
asosData["valid"] = asosData["valid"].str.slice(0,11)
asosData = asosData[asosData["time"] == "12"]
asosData = asosData.drop_duplicates(subset=["station", "valid"])

# read our metadata
asosMetadata = pd.read_csv("asosMetadata.csv").drop("wxcodes", axis=1)
convertDataTypes(asosMetadata)
asosMetadata = asosMetadata.drop_duplicates(subset=["station"])
# open the schemas file
# schemas = open("schemas.sql", "w")
#
try:
    coopData.to_sql(name='coopdata', con=conn)
    print(f"Inserted {len(coopData)} rows of COOP data!")
    # schemas.write(pd.io.sql.get_schema(coopData, 'coopdata', con=conn))
except:
    print("Could not insert COOP data - maybe you've already done it?")

try:
    coopMetadata[0].to_sql(name='coopmetadata', con=conn)
    print(f"Inserted {len(coopMetadata[0])} rows of COOP metadata!")
    # schemas.write(pd.io.sql.get_schema(coopMetadata[0], 'coopmetadata', con=conn))
except:
    print("Could not insert COOP metadata - maybe you've already done it?")

try:
    asosData.to_sql(name='asosdata', con=conn)
    print(f"Inserted {len(asosData)} rows of ASOS data!")
    # schemas.write(pd.io.sql.get_schema(asosData, 'asosdata', con=conn))
except Exception as e:
    print(e, "Could not insert ASOS data - maybe you've already done it?")

try:
    asosMetadata.to_sql(name='asosmetadata', con=conn)
    print(f"Inserted {len(asosMetadata)} rows of ASOS metadata!")
    # schemas.write(pd.io.sql.get_schema(asosMetadata, 'asosmetadata', con=conn))
except:
    print("Could not insert ASOS metadata - maybe you've already done it?")

# schemas.close()
