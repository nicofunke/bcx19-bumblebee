import pandas as pd
import json
import requests
import numpy as np
from datetime import date, datetime
from flask import Flask

parcels = np.arange(10,55)
sick_parcels = []

for parcel in parcels:
    df = pd.DataFrame()
    parcel_query = f"https://esa-api.geocledian.com/agknow/api/v3/parcels/%s/ndvi?key=a467adbd-8b10-4526-9d50-8fa119b1b4fb&statistics=true" % parcel
    response = requests.get(parcel_query).json()

    if response['content'] == 'Parcel id not available':
        continue

    dates = []
    for i in np.arange(0, len(response['content'])):
        date_string = response['content'][i]['date']
        dates.append(date(*map(int, (date_string.split("-")))))
    bounds_vals = []
    for i in np.arange(0, len(response['content'])):
        # first point
        p_x = response['content'][i]['bounds'][0][0]
        p_y = response['content'][i]['bounds'][0][1]
        # second point
        q_x = response['content'][i]['bounds'][1][0]
        q_y = response['content'][i]['bounds'][1][1]
        # average point
        x = (p_x + q_x)/2
        y = (p_y + q_y)/2
        bounds_vals.append([x,y])
    ndvi_vals = []
    for i in np.arange(0, len(response['content'])):
        ndvi_vals.append(response['content'][i]['statistics']['mean'])
    df['dates'] = dates
    df['location'] = bounds_vals
    df['ndvi'] = ndvi_vals
    df['parcel_id'] = parcel
    latest_day = np.array(dates).max()
    latest_ndvi = df[df.dates == latest_day]['ndvi'][0]
    latest_location = df[df.dates == latest_day]['location'][0]
    current_parcel_id = parcel
    if latest_ndvi < 0.4:
	sick_parcels.append({'id': parcel, 'date': latest_day.isoformat(), 'location': latest_location, 'ndvi': latest_ndvi })

sick_parcels = pd.DataFrame(sick_parcels).set_index('id').T.to_json()

app = Flask(__name__)

@app.route('/')
def index():
  return sick_parcels

@app.route('/greet')
def say_hello():
  return 'Hello from Server'
