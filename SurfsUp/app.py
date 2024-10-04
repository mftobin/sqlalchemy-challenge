# Import the dependencies.
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_
# added and_ for the final route so I could filter by two dates

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`

Measurement = Base.classes.measurement

Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

#summary of all the routes:
@app.route('/')
def welcome():
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>precipitation routes</a><br/>"
        f"<a href='/api/v1.0/stations'>stations routes</a><br/>"
        f"<a href='/api/v1.0/tobs'>tops routes</a><br/>"
        "<a href='/api/v1.0/{start}'>YYYY-MM-DD to end of data</a> (enter %YYYY-MM-DD%)<br/>"
        "<a href='/api/v1.0/{start}/{end}'>YYYY-MM-DD to YYYY-MM-DD</a> (enter %YYYY-MM-DD/YYYY-MM-DD%)<br/>"
    )
# A precipitation route that:
# Returns json with the date as the key and the value as the precipitation (3 points)
# Only returns the jsonified precipitation data for the last year in the database (3 points)

@app.route("/api/v1.0/precipitation")
def precipitation():
    precip_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= "2016-08-23").all()
    clean_data = {}

    for date_prcp in precip_results:

    # date_prcp = precip_results[0]
        clean_data [date_prcp[0]] = date_prcp[1]

    session.close()

    return jsonify(clean_data)

# A stations route that:
# Returns jsonified data of all of the stations in the database (3 points)
@app.route("/api/v1.0/stations")
def stations():
      stations_results = session.query(Station.station, Station.name).all()
      stations_results = pd.DataFrame(stations_results).to_dict("records")
      session.close()
      return jsonify(stations_results)

# A tobs route that:
# Returns jsonified data for the most active station (USC00519281) (3 points)
# Only returns the jsonified data for the last year of data (3 points)
@app.route("/api/v1.0/tobs")
def tobs():
    most_active_station = session.query(Measurement.tobs).filter(Measurement.date >= "2016-08-23").filter(Measurement.station == "USC00519281").order_by(Measurement.tobs.asc()).all()
    clean_data = [row[0] for row in most_active_station]
    session.close()
    return jsonify(clean_data)

# API Dynamic Route (15 points)
# To receive all points, your Flask application must include

# A start route that:
# Accepts the start date as a parameter from the URL (2 points)
# Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset (4 points)
@app.route("/api/v1.0/<start>")
def start_route(start):
    date_to_end_data = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(Measurement.date >= start
    ).first()  # Get the first result as a single tuple

    # Check if data is returned
    if date_to_end_data:
        clean_data = {
            "Minimum Temperature": date_to_end_data[0],
            "Maximum Temperature": date_to_end_data[1],
            "Average Temperature": date_to_end_data[2]
        }
    else:
        clean_data = {
            "error": "No data found for the specified date range."
        }
    session.close()
    return jsonify(clean_data)

# A start/end route that:
# Accepts the start and end dates as parameters from the URL (3 points)
# Returns the min, max, and average temperatures calculated from the given start date to the given end date (6 points)

@app.route("/api/v1.0/<start>/<end>")
def start_end_route(start, end):
    # Query to get min, max, and avg temperatures for the specified date range
    date_range_data = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ).filter(
        and_(Measurement.date >= start, Measurement.date <= end)
    ).first()  # Get the first result as a single tuple

    # Check if data is returned
    if date_range_data:
        clean_data = {
            "Minimum Temperature": date_range_data[0],
            "Maximum Temperature": date_range_data[1],
            "Average Temperature": date_range_data[2]
        }
    else:
        clean_data = {
            "error": "No data found for the specified date range."
        }

    session.close()
    return jsonify(clean_data)

if __name__ == '__main__':
    app.run(debug=True)