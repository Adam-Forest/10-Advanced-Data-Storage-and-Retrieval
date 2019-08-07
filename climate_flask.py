# import Flask and JSON dependencies
from flask import Flask, jsonify
import datetime
import json

# import utilities

from dateutil.relativedelta import relativedelta

# import ORM stuff
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# get current time for log
currentDT = datetime.datetime.now()

# Set up database connections
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

## gather some date information
session = Session(engine)
# query min and max dates make last_day datetime
date_range = session.query(func.max(Measurement.date).label("last_day"),func.min(Measurement.date).label("first_day"))
last_day=datetime.datetime.strptime(date_range[0].last_day, '%Y-%m-%d')
first_day=datetime.datetime.strptime(date_range[0].first_day, '%Y-%m-%d')

# Calculate the date 1 year ago from the last data point in the database
date_12_months_ago = last_day - relativedelta(months=12)
date_12_months_ago
session.close()

app = Flask(__name__)

# open and closing tags for html doc
head_html="<!DOCTYPE html><html><head><title>Climate Flask API</title></head><body>"
foot_html="</body></html>"

# navigation hints for APIT
nav_html = "<div><span style='font-weight:bold;'>Available API endpoints, response is in JSON:</span>\
<ul>\
<li><a href='/api/v1.0/precipitation'>precipitation ( /api/v1.0/precipitation )</a></li>\
<li><a href='/api/v1.0/stations'>stations ( /api/v1.0/stations )</a></li>\
<li><a href='/api/v1.0/tob'>TOB tempurature ( /api/v1.0/tob )</a></li>\
<li>replace start and with ISO dates YYYY-MM-DD ( /api/v1.0/&lt;start date&gt; )</li>\
<li>replace start and end date with ISO dates YYYY-MM-DD ( /api/v1.0/&lt;start date&gt;/&lt;end date&gt; )</li>\
</ul>\
</div>"

# create root
@app.route("/")
def home():
    print(str(currentDT) + " - Log: root request")
    return head_html + nav_html + foot_html

@app.route("/api/v1.0/precipitation")
def precipitation():
    print(str(currentDT) + " - Log: precipitation request")
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query percipitation values
    session = Session(engine)
    results = session.query(Measurement.date,Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    all_percip = []
    for date, prcp in results:
        percip_dict = {}
        percip_dict[date] = prcp
        all_percip.append(percip_dict)
    return jsonify(all_percip)

@app.route("/api/v1.0/stations")
def stations():
    print(str(currentDT) + " - Log: stations request")
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query station values
    session = Session(engine)
    results = session.query(Station.id,Station.name).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    all_stations = []
    for id, name in results:
        station_dict = {}
        station_dict[id] = name
        all_stations.append(station_dict)
    return jsonify(all_stations)

@app.route("/api/v1.0/tob")
def tob():
    print(str(currentDT) + " - Log: tob request")
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query using date variables set above, adjust so between between
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date.between(date_12_months_ago - relativedelta(days=1), last_day + relativedelta(days=1)))
    session.close()

    # Create a dictionary from the row data and append to a list
    filtered_tob = []
    for date, tob in results:
        tob_dict = {}
        tob_dict[date] = tob
        filtered_tob.append(tob_dict)
    return jsonify(filtered_tob)

@app.route("/api/v1.0/<start>")
def daterangestart(start=None):
    print(str(currentDT) + " - Log: start date range request")
    # check that date is properly formatted
    try:
        start = datetime.datetime.strptime(start, '%Y-%m-%d')
    except:
        return("Incorrect start date, format should be YYYY-MM-DD")
    # open session get results from start to last date (last_day)
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs),func.round(func.avg(Measurement.tobs),1),func.max(Measurement.tobs)).filter(Measurement.date.between(start - relativedelta(days=1), last_day + relativedelta(days=1)))
    session.close()

    filtered_tob = []
    for mint, avgt, maxt in results:
        tob_dict = {}
        tob_dict["Min Temp"] = mint
        tob_dict["Avg Temp"] = avgt
        tob_dict["Max Temp"] = maxt
        filtered_tob.append(tob_dict)
    return jsonify(filtered_tob)


@app.route("/api/v1.0/<start>/<end>")
def daterangestartend(start=None, end=None):
    print(str(currentDT) + " - Log: date range request")

    # check that date is properly formatted
    try:
        start = datetime.datetime.strptime(start, '%Y-%m-%d')
    except:
        return("Incorrect start date, format should be YYYY-MM-DD")

    try:
        end = datetime.datetime.strptime(end, '%Y-%m-%d')
    except:
        return("Incorrect start date, format should be YYYY-MM-DD")
    
    # open session get results from start to last date (last_day)
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs),func.round(func.avg(Measurement.tobs),1),func.max(Measurement.tobs)).filter(Measurement.date.between(start - relativedelta(days=1), end + relativedelta(days=1)))
    session.close()

    filtered_tob = []
    for mint, avgt, maxt in results:
        tob_dict = {}
        tob_dict["Max Temp"] = maxt
        tob_dict["Avg Temp"] = avgt
        tob_dict["Min Temp"] = mint
        filtered_tob.append(tob_dict)
    return jsonify(filtered_tob)

if __name__ == "__main__":
    app.run(debug=True)
