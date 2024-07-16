import json
import plotly
import pandas as pd
from flask import Flask, render_template, request, jsonify
from plotly.graph_objs import Bar, Scatter
import webbrowser
import plotly.io as pio
import joblib
import numpy as np
import os

try:
    import pyarrow

except ImportError:
    os.system('python -m pip install pyarrow')

from sqlalchemy import create_engine

app = Flask(__name__)

pio.templates.default = 'seaborn'

# Load data
print('Loading Data')
engine = create_engine('sqlite:///data/weather_data.db')
df = pd.read_sql_table('weather_data_daily', engine)
df1 = pd.read_sql_table('weather_data_yearly', engine)

print('Data Loaded Successfully !')

# create a selection of countries from the df
unique_countries = df1['country'].unique()
# Insert an empty value to show the global temperature
unique_countries = np.insert(unique_countries, 0, 'Global Data')

# Load prediction model
model = joblib.load("models/weather_model.pkl")
print('model imported')




# # Index webpage displays visualization of weather and other data
@app.route('/')
@app.route('/index')

def index():
    
    #Get user selection from dropdown of country
    country = request.args.get('country')

    #Extract data needed for visuals
    #by starting the webpage, if there is no country selected or the selection is Global Data, show the visualization for the world.
    if country is None or country =='Global Data':
        temp_year = df1.groupby('year')['avg_temp_c'].mean().index
        avg_temp = df1.groupby('year')['avg_temp_c'].mean().values
        max_temp = df1.groupby('year')['max_temp_c'].mean().values
        min_temp = df1.groupby('year')['min_temp_c'].mean().values
        CO2_year = df1.groupby('year')['co2'].sum().index
        CO2_values = df1.groupby('year')['co2'].sum().values
        pop_year = df1.groupby('year')['population'].sum().index
        pop_values = df1.groupby('year')['population'].sum().values
    
    else:
        temp_year = df1[df1['country'] == country].groupby('year')['avg_temp_c'].mean().index
        avg_temp = df1[df1['country'] == country].groupby('year')['avg_temp_c'].mean().values
        max_temp = df1[df1['country'] == country].groupby('year')['max_temp_c'].mean().values
        min_temp = df1[df1['country'] == country].groupby('year')['min_temp_c'].mean().values
        CO2_year = df1[df1['country'] == country].groupby('year')['co2'].sum().index
        CO2_values = df1[df1['country'] == country].groupby('year')['co2'].sum().values
        pop_year = df1[df1['country'] == country].groupby('year')['population'].sum().index
        pop_values = df1[df1['country'] == country].groupby('year')['population'].sum().values


    # Create visuals
    graphs = [
        {
            'data': [
                Scatter(
                    x=temp_year,
                    y=avg_temp,
                    mode='lines',
                    name='Average Temperatures'

                ),
                Scatter(
                    x=temp_year,
                    y=max_temp,
                    mode='lines',
                    name='Max Temperatures'
                ),
                Scatter(
                    x=temp_year,
                    y=min_temp,
                    mode='lines',
                    name='Min Temperatures',
                ),
                
            ],
            'layout': {
                
                'title': f'{country} Temperature Trends' if country else 'Global Temperature Trends',
                'yaxis': {'title': "Temperature (C)", 'tickfont':{'size':'12'}},
                'xaxis': {'title': "Year", 'tickfont':{'size':'12'}},
                'font':{'family':'Segoe UI', 'size':'20','color':'e5e0e0'},
                'plot_bgcolor':'#0e0d0d',
                'paper_bgcolor':'#0e0d0d',
                'width':'85%',
                'height':'85%'

            }
        },
        {
            'data': [
                Bar(
                    x=CO2_year,
                    y=CO2_values,
                    name='CO2 Evolution'

                )
                
            ],
            'layout': {
                'title': f'{country} CO2 Emissions Evolution' if country else 'Global CO2 Emissions Evolution',
                'yaxis': {'title': "CO2 in Thousand Tones", 'tickfont':{'size':'12'}},
                'xaxis': {'title': "Year", 'tickfont':{'size':'12'}},
                'font':{'family':'Segoe UI', 'size':'20','color':'e5e0e0'},
                'plot_bgcolor':'#0e0d0d',
                'paper_bgcolor':'#0e0d0d'
            }
        },
        {
            'data': [
                Bar(
                    x=pop_year,
                    y=pop_values,
                    name='Population Evolution'

                )
                
            ],
            'layout': {
                'title': f'{country} Population Evolution' if country else 'Global Population Evolution',
                'yaxis': {'title': "Population", 'tickfont':{'size':'12'}},
                'xaxis': {'title': "Year", 'tickfont':{'size':'12'}},
                'font':{'family':'Segoe UI', 'size':'20','color':'e5e0e0'},
                'plot_bgcolor':'#0e0d0d',
                'paper_bgcolor':'#0e0d0d'

            }
        }
    ]
    
    #Encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    #get the user input from the web application
    year = request.args.get('year')
    co2 = request.args.get('co2')
    pop_diff = request.args.get('pop_diff')
    prec_mm = request.args.get('prec_mm')


    #Convert parameters to appropriate types
    year = int(year) if year else None
    co2 = float(co2) if co2 else None
    pop_diff = float(pop_diff) if pop_diff else None
    prec_mm = float(prec_mm) if prec_mm else None

    #Calculate information for prediction definition
    max_year = df1[df1['year'] == df1['year'].max()]['year'].unique()[0]
    sum_co2 = df1[df1['year']==max_year]['co2'].sum()
    sum_pop = df1[df1['year']==max_year]['population'].sum()

    #weather_data_yearly[['year','co2','population_diff','co2_growth_prct','precipitation_mm','population']]

    #If no prediction is available, do not show results. If yes, proceed with calculation
    prediction = None
    if year is not None and co2 is not None and pop_diff is not None:
        #Use the User Input in order to define the prediction
        prediction = model.predict(np.array([[year, sum_co2+(sum_co2 * (co2 / 100)), pop_diff, (co2*100), prec_mm, sum_pop+pop_diff ]]))[0]
        #Split the prediction from the model to 3 values rounded to 2 decimals
        prediction = [round(prediction[0],2), round(prediction[1],2), round(prediction[2],2)]


    # Render web page with plotly graphs
    return render_template('home.html', ids=ids, graphJSON=graphJSON, countries=unique_countries, predictions=prediction, selected_country = country)


def main():
    webbrowser.open_new("http://127.0.0.1:3000/")
    app.run(host='127.0.0.1', port=3000, debug=True)
    

if __name__ == '__main__':
    main()

