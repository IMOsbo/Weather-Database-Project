# coding: utf-8
import pandas as pd

# ## For ASOS data
# data = pd.read_csv("asos.csv")
# # data["valid"].dtype
# # data["valid"].str.slice(11,12)
# # data["valid"].str.slice(11,13)
# # data["time"] = data["valid"].str.slice(11,13)
# # data
# # data = data[data["time"] == "12"]
# # data
# pd.DataFrame(data.columns).to_html("asos_col.html")
# ### Endasos


### Check the COOP data coluumn         
df_coop=pd.read_csv('asos.csv')
df_coop
pd.DataFrame(df_coop.columns).to_html("asos_col.html")