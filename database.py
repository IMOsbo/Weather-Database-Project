# coding: utf-8
import mysql.connector
from sqlalchemy import create_engine
import pandas as pd

USER = "root"
PW = "1234"
# run create database weather;
DATABASE = "weather"

conn = create_engine(f"mysql+mysqlconnector://{USER}:{PW}@127.0.0.1/{DATABASE}")

data = pd.read_html("https://mesonet.agron.iastate.edu/sites/networks.php?network=TN_COOP&format=html&nohtml=on")


data[0].to_sql(name='coopmetadata', con=conn)
