# coding: utf-8
import pandas as pd
from IPython import get_ipython
data = pd.read_csv("asos.csv")
data
data["valid"].dtype
data["valid"].str.slice(11,12)
data["valid"].str.slice(11,13)
data["time"] = data["valid"].str.slice(11,13)
data
data = data[data["time"] == "12"]
data
data.to_csv("filteredasosdata.csv", index=False)
#get_ipython().run_line_magic('export', '')
#get_ipython().run_line_magic('tofile', '')
#get_ipython().run_line_magic('save', '')
