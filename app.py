# Import the dependencies.
import numpy as np
import re
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
from sqlalchemy.sql import exists  

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/sophi/OneDrive/Desktop/ClassFolder/sqlalchemy-challenge/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
station=Base.classes.station
measurement=Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    """List all available API Routes"""
    return(
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/<start><br/>'
        f'/api/v1.0/<start>/<end>'
    )
@app.route('/api/v1.0/precipitation')
def precipitation():

    #retrieve only the last 12 months of data of precipitation
    most_recent_date=session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_year_date=dt.date(2017, 8, 23)-dt.timedelta(days=365)
    precipitation=session.query(measurement.date, measurement.prcp).filter(measurement.date >= last_year_date).all()
    #Create dictionary 
    precipitation_list = []

    for row in precipitation:
        date_dict = {}
        date_dict[row.date] = row.prcp
        precipitation_list.append(date_dict)
    
    #Return to api
    return jsonify(precipitation_list)

@app.route('/api/v1.0/stations')
def stations():

    #Query stations
    results = session.query(station.station).all()

    #Convert to normal list
    station_info= list(np.ravel(results))
    
    return jsonify(station_info)

@app.route('/api/v1.0/tobs')
def tobs():
    
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_year_date=dt.date(2017, 8, 23)-dt.timedelta(days=365)

    #Query the dates and temperature observations of the most-active station for the previous year of data.
    most_active_station = session.query(measurement.date, measurement.tobs) \
        .filter(measurement.date >= last_year_date) \
        .filter(measurement.station == 'USC00519281') \
        .all()
    
    #Convert to normal list
    most_active_info = list(np.ravel(most_active_station))
    
    return jsonify(most_active_info)

@app.route("/api/v1.0/<start>")
def temp_range_start(start):
    
    #Query to get the min, max, average for specified date
    results = session.query(measurement.date, func.avg(measurement.tobs), func.max(measurement.tobs), func.min(measurement.tobs)) \
                     .filter(measurement.date >= start) \
                     .group_by(measurement.date) \
                     .all()

    session.close()

    # Create a dictionary and append
    temp = []
    for date, avg, max, min in results:
        temp_dict = {}
        temp_dict['Date'] = date
        temp_dict['TAVG'] = avg
        temp_dict['TMAX'] = max
        temp_dict['TMIN'] = min
        
        
        temp.append(temp_dict)

    return jsonify(temp)

@app.route("/api/v1.0/<start>/<end>")
def temp_range_start_end(start, end):
    
    #Query to get the min, max, average for date ranges
    results = session.query(measurement.date, func.avg(measurement.tobs), func.max(measurement.tobs), func.min(measurement.tobs))\
                    .filter(measurement.date >= start, measurement.date <= end)\
                    .group_by(measurement.date)\
                    .all()
    
    session.close()
    
    # Create a dictionary and append
    temp = []
    for date, avg, max, min in results:
        temp_dict = {}
        temp_dict['Date'] = date
        temp_dict['TAVG'] = avg
        temp_dict['TMAX'] = max
        temp_dict['TMIN'] = min


        temp.append(temp_dict)

    return jsonify(temp)

#Call Flask to run
if __name__ == '__main__':
    app.run(debug=True)

