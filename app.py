# 1. import Flask
from flask import Flask,jsonify
import pandas as pd
import numpy as np
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect,func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# 2. Create an app, being sure to pass __name__
app = Flask(__name__)
# reflect an existing database into a new model
Base=automap_base()
# reflect the tables
Base.prepare(engine,reflect=True)

MSM=Base.classes.measurement
stations=Base.classes.station

session=Session(engine)
# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return ("Available routes: <br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start-date (in the form of YYYY-MM-DD) <br/>"
        "/api/v1.0/start-date/end-date (in the form of YYYY-MM-DD)")


#query last 12 months date and preciptitaion as a dictionry and display as JSON
@app.route("/api/v1.0/precipitation")
def prcp():
    last12month_results=session.query(func.strftime("%Y-%m-%d", MSM.date),MSM.prcp).\
              filter(func.strftime("%Y-%m-%d", MSM.date)>=dt.date(2016,8,23)).all()
    session.close()
    
    prcp_dict={}
    for row in last12month_results:
        prcp_dict[row[0]]=row[1]
    return jsonify(prcp_dict)

#return a JSON list of stations
@app.route("/api/v1.0/stations")
def station():
    station_results=session.query(stations.station,stations.name).all()
    session.close()
    
    station_dict={}
    station_dict['Station']='Name'
    for row in station_results:
        station_dict[row[0]]=row[1]
    return jsonify(station_dict)

#return a JSON list of temperature observations for the last year
@app.route("/api/v1.0/tobs")
def tobs():
    tobs_results=session.query(func.strftime("%Y-%m-%d", MSM.date),MSM.tobs).\
              filter(func.strftime("%Y-%m-%d", MSM.date)>=dt.date(2016,8,23)).all()
    session.close()
    
    temp_list=[]
    
    for item in tobs_results:
        temp_list.append(item[1])
    return jsonify(temp_list)


@app.route("/api/v1.0/<start>")
def start_func(start):
    onedate_result=session.query(func.min(MSM.tobs), func.avg(MSM.tobs), func.max(MSM.tobs)).\
        filter(MSM.date>= start).all()
    session.close()
    
    onedate_list=list(np.ravel(onedate_result))

    return (f"From {start} to the last date: <br/>"
            f"The min temp was: {onedate_list[0]} degrees; <br/>"
            f"The averate temp was: {onedate_list[1]} degress; <br/>"
            f"The max temp was: {onedate_list[2]} degress; <br/>")

@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start,end):    
    twodates_result=session.query(func.min(MSM.tobs), func.avg(MSM.tobs), func.max(MSM.tobs)).\
        filter(MSM.date >= start).\
        filter(MSM.date <= end).all()
    session.close()
    
    twodates_list=list(np.ravel(twodates_result))

    return (f"From {start} to {end}: <br/>"
            f"The min temp was: {twodates_list[0]} degrees; <br/>"
            f"The averate temp was: {twodates_list[1]} degress; <br/>"
            f"The max temp was: {twodates_list[2]} degress; <br/>")
          

if __name__ == "__main__":
    app.run(debug=True)
