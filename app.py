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

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)

#Setup the welcome or home page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/measurement<br/>"
        f"/api/v1.0/precipitation<br/>"
    )

#Setup the station page
@app.route("/api/v1.0/station")
def stations():
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

#Setup the precipitation page
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #First we can use strftime and some functions to find the most recent date
    top_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date)))

    #From this we can pull out out a a string of the date
    top_date_date = dt.datetime.strptime(top_date[0][0], "%Y-%m-%d")

    #Now I need a variable that is the date 1 year ago. I used weeks=52.2 since 52*7 /= 365
    year_ago = top_date_date - dt.timedelta(weeks=52.2)



    # Query all stations
    #results = session.query(Station.station).all()
    qry = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date >= year_ago).all()

    #prcp_list = []
    prcpDict = {}
    for result in qry:
        prcpDict.update({result.date:result.prcp})

    return jsonify(prcpDict)

#Setup the stations page
@app.route("/api/v1.0/stations")
def stations():


if __name__ == "__main__":
    app.run(debug=True)
