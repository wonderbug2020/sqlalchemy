# Import the needed libraries
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#Next to setup  the Database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#Create an app,
app = Flask(__name__)

#Setup the welcome or home page
@app.route("/")
def welcome():
    #Need to return all the possible routes
    return (
        f"Available Routes:<br/>"
        #f"/api/v1.0/station<br/>"
        #f"/api/v1.0/measurement<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/*<start><br/>"
        f"/api/v1.0/*/#<start><br/>"
        f"* is a starting date<br/>"
        f"# is an end date"
    )
"""
#Setup the station page
@app.route("/api/v1.0/station")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    qry_result = list(np.ravel(results))

    return jsonify(qry_result)

#Setup the measurement page
@app.route("/api/v1.0/measurement")
def measurement():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Measurement.prcp).all()

    session.close()

    # Convert list of tuples into normal list
    qry_result = list(np.ravel(results))

    return jsonify(qry_result)
"""

#Setup the precipitation page
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #First we can use strftime and some functions to find the most recent date in the database
    top_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date)))

    #From this we can pull out out a string of the date
    top_date_date = dt.datetime.strptime(top_date[0][0], "%Y-%m-%d")

    #Now I need a variable that is the date 1 year ago. I used weeks=52.2 since 52*7 /= 365
    year_ago = top_date_date - dt.timedelta(weeks=52.2)



    # Query all stations
    #results = session.query(Station.station).all()
    qry = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date >= year_ago).all()

    session.close()

    #prcp_list = []
    prcpDict = {}
    for result in qry:
        prcpDict.update({result.date:result.prcp})

    return jsonify(prcpDict)

#Setup the stations page
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    qry_result = list(np.ravel(results))

    return jsonify(qry_result)

#Setup the tobs page
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Make a query to find the activity of each station reporting
    qry_station_active = session.query(Measurement.station, func.count(Measurement.station)).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).all()

    session.close()

    #The first entry is the most active since this is descending order
    most_active = qry_station_active[0][0]

    #First to set the string of the return from some functions to variables
    last_date_str = last_date()

    #Now I need a variable that is the date 1 year ago. I used weeks=52.2 since 52*7 /= 365
    year_ago = last_date_str - dt.timedelta(weeks=52.2)

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Measurement.date, Measurement.tobs).\
                     filter(Measurement.date >= year_ago).\
                     filter(Measurement.station == most_active).all()

    session.close()

    # Convert list of tuples into normal list
    qry_result = list(np.ravel(results))

    return jsonify(qry_result)

@app.route("/api/v1.0/<start>")
def start_date(start):
    #First to set the string of the return from some functions to variables
    first_date_str = str(first_date())
    last_date_str = str(last_date())

    #Next is an if statement to check to see if the date passed is between the appropriate dates
    if (start < first_date_str) | (start > last_date_str):
        return("please choose a date between 2010-01-02 and 2017-08-23")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query to get the desired data
    temperature_readings = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.round(func.avg(Measurement.tobs),1)).\
                                     filter(Measurement.date >= start).all()

    session.close()

    qry_result = list(np.ravel(temperature_readings))

    return jsonify(qry_result)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    #First to set up an if statement to make sure the end date comes after the start date
    if start >= end:
        return("please set your end date to be after the beginning date")

    #Second, to set the string of the return from some functions to variables
    first_date_str = str(first_date())
    last_date_str = str(last_date())

    #Next is an if statement to check to see if the date passed is between the appropriate dates
    if (start < first_date_str) | (end > last_date_str):
        return("please choose a set of dates between 2010-01-02 and 2017-08-23")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query to get the desired data
    temperature_readings = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.round(func.avg(Measurement.tobs),1)).\
                                     filter(Measurement.date >= start).\
                                     filter(Measurement.date <= end).all()

    session.close()

    qry_result = list(np.ravel(temperature_readings))

    return jsonify(qry_result)

#Now What I want to do is have some functions that will be used several times
#First up is a function that will find the first date of the database
def first_date():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #First we can use strftime and some functions to find the most recent date in the database
    first_date = session.query(func.min(func.strftime("%Y-%m-%d", Measurement.date)))

    #From this we can pull out out a string of the date
    first_date_str = dt.datetime.strptime(first_date[0][0], "%Y-%m-%d")

    #Now to return the date string
    return(first_date_str)

#Second is going to be a function that will find the last date of the database
def last_date():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #First we can use strftime and some functions to find the most recent date in the database
    last_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date)))

    #From this we can pull out out a string of the date
    last_date_str = dt.datetime.strptime(last_date[0][0], "%Y-%m-%d")

    #Now to return the date string
    return(last_date_str)

if __name__ == "__main__":
    app.run(debug=True)
