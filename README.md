# Weather Database Project

# 🌦️🌤️💻

Welcome to our CSCI 4560/5560 Database project!


## Data Sources

Data comes from IOWA Mesonet, specifically COOP and ASOS.

Here's the URLs to look at:


### COOP Metadata

<https://mesonet.agron.iastate.edu/sites/networks.php?network=TN_COOP&format=html&nohtml=on>

It's all HTML, so we should be able to use `pd.read_html` for this really well... <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_html.html>



### ASOS Data

To request 1 ASOS station:

<https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=MBT&data=all&year1=2023&month1=10&day1=10&year2=2023&month2=10&day2=10&tz=Etc%2FUTC&format=onlycomma&latlon=yes&elev=yes&missing=M&trace=T&direct=no&report_type=3&report_type=4>


Important notes here: 

- Encodes missing data as "M"
- Trace data is "T" - maybe just get rid of it?

Here's the URL to _technically_ pull them all:

### ASOS Metadata

So, our data for ASOS actually includes all of the metadata all ready, which is really nice...

[Really loooooooooooooooong link for all the data](https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?station=MBT&station=MOR&station=0A9&station=1M5&station=2A0&station=2M2&station=8A3&station=BGF&station=BNA&station=CHA&station=CKV&station=CSV&station=DKX&station=DYR&station=FYE&station=FYM&station=GCY&station=GKT&station=GZS&station=HZD&station=JAU&station=JWN&station=LUG&station=M01&station=M02&station=M04&station=M08&station=M33&station=M54&station=M91&station=MBT&station=MEM&station=MKL&station=MMI&station=MNV&station=MOR&station=MQY&station=MRC&station=NQA&station=OQT&station=PHT&station=PVE&station=RKW&station=RNC&station=RZR&station=SCX&station=SNH&station=SRB&station=SYI&station=SZY&station=THA&station=TRI&station=TYS&station=UCY&station=XNX&data=all&year1=2023&month1=10&day1=10&year2=2023&month2=10&day2=10&tz=Etc%2FUTC&format=onlycomma&latlon=yes&elev=yes&missing=M&trace=T&direct=no&report_type=3&report_type=4)

Nobody's got time for that... 🙄

Probably going to be `pd.read_csv` for this one <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html>

## Data Limits

Not sure what dates we want to use yet? 

- I'm thinking something like Jan 1 2023 - September 31 2023?
- That's enough data to be interesting, but not so much to be troublesome...

## What about SQL?

I mean, this is a class about SQL after all...

So, it turns out Pandas can generate your schemas for you:

<https://stackoverflow.com/a/31075679>

Yay! This gets us our actual schemas with ~~little~~ no work on our part :)

Once we get our data, we can insert it into our tables too.

* <https://docs.sqlalchemy.org/en/20/core/engines.html>
* <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html>


