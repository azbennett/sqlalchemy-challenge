# Import the dependencies.
import numpy as np
import pandas as pd
import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func



from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    #List all routes
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitation 
    oneyearback = datetime.date(2017, 8, 23) - datetime.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= oneyearback).all()
    session.close()

    # Convert list of tuples into normal list
    all_data = []

    for date, prcp in results:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        all_data.append(precip_dict)

    return jsonify(all_data)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitation 
    results = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)    

#Query the dates and temperature observations of the most-active station for the previous year of data.
#Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitation 
    oneyearback = datetime.date(2017, 8, 23) - datetime.timedelta(days=365)
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == 'USC00519281', Measurement.date >= oneyearback)\
        .all()
    
    session.close()

    # Convert list of tuples into normal list
    one_year_tobs_data = []
    
    for station, date, tobs in results:
        tobs_dict = {}
        tobs_dict["Station"] = station
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        one_year_tobs_data.append(tobs_dict)

    return jsonify(one_year_tobs_data)    

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/<start>")
def startdata(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query and error checking
    try:
        date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    except ValueError:
        date = datetime.datetime.strptime(start, "%y-%m-%d").date()

    results = session.query(func.min(Measurement.tobs).label("Min"),func.max(Measurement.tobs).label("Max"),func.avg(Measurement.tobs).label("Avg")).filter(Measurement.date >= date).first()
    
    session.close()
    
    #Labels the future JSON info

    start_date_data = {
        "Min": results[0],
        "Max": results[1],
        "Avg": results[2]
    }

    return jsonify(start_date_data)    

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>/<end>")
def startenddata(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query and error checking
    try:
        date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
        date2 = datetime.datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        date = datetime.datetime.strptime(start, "%y-%m-%d").date()
        date2 = datetime.datetime.strptime(end, "%y-%m-%d").date()


    results = session.query(func.min(Measurement.tobs).label("Min"),func.max(Measurement.tobs).label("Max"),func.avg(Measurement.tobs).label("Avg")).filter(Measurement.date >= date, Measurement.date <= date2).first()
        
    session.close()
    
    #Labels the future JSON info
    start_date_data = {
        "Min": results[0],
        "Max": results[1],
        "Avg": results[2]
    }
    return jsonify(start_date_data)    

if __name__ == '__main__':
    app.run(debug=True)


#datetime string convert: https://stackoverflow.com/questions/53460391/passing-a-date-as-a-url-parameter-to-a-flask-route
#fixing my datetime.datetime.strptime() https://stackoverflow.com/questions/12070193/why-does-trying-to-use-datetime-strptime-result-in-module-object-has-no-at

