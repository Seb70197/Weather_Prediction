#Importing necessary libraries
import pandas as pd
import numpy as np
import pip
import os
import datetime as dt
from datetime import datetime


try:
    import pyarrow
except ImportError:
    os.system('python -m pip install pyarrow')

import pyarrow


def load_data():
    """loading the available data used for the webapplication before clean-up
    Return : 4 Dataframe to be saved for utilization within the model"""
    #weather data containing the weather evolution & data
    weather_data = pd.read_parquet('data/daily_weather.parquet', engine='pyarrow')
    #loading cities and countries to identify the location of the weather station around the world
    countries = pd.read_csv('data/countries.csv')
    #loading CO2 and Energy emission around the world per month
    co2_emission = pd.read_csv('data/owid-co2-data.csv')
    #load json station information
    station_info = pd.read_json('data/full.json')
    #correct name of station id
    station_info['name'] = pd.json_normalize(station_info['name'])['en']
    #keep only relevant columns for merging with weather_data
    station_info = station_info[['id','country','name']]

    return weather_data, countries, co2_emission, station_info


def clean_data(weather_data, countries, co2_emission, station_info):
    """Cleaning the Data
    
    Arg: Weather Data loaded, countries Information, co2 emission information, station location information
    
    Return : Cleaned Data saved within 2 dataframe to be saved later on DataBase"""

    import pandas as pd
    import numpy as np
    import datetime as dt
    from datetime import datetime
    
    #transform the date to ensure filters and selection are working correctly
    weather_data['date'] = pd.to_datetime(weather_data['date'], dayfirst=True)
    #limiting the dataframe to the dates of choice
    weather_data = weather_data[(weather_data['date']>=pd.to_datetime('01.01.1970', dayfirst=True)) & (weather_data['date']<=pd.to_datetime('31.12.2022', dayfirst=True))]
    #Getting only the rows for which the data are present
    weather_data = weather_data.dropna(subset=['avg_temp_c','min_temp_c','max_temp_c','precipitation_mm'])
    #Limit the dataframe to the desired columns
    weather_data = weather_data[['station_id','city_name','date','season','avg_temp_c','min_temp_c','max_temp_c','precipitation_mm']]

    #merging new country and station 
    weather_data = weather_data.merge(station_info, right_on='id',left_on='station_id')
    #drop the old columns and rename
    weather_data = weather_data.drop(columns='city_name').rename(columns={'country_y':'country','name_y':'station_name'})

    #drop duplicates from countries (GB duplicated)
    countries = countries.drop_duplicates(subset='iso2', keep='first')

    #final weather data daily
    weather_data_daily = weather_data.merge(countries[['iso2','country','region', 'continent']], left_on='country',right_on='iso2', how='left')
    #creating columns for Year
    weather_data_daily['year'] = weather_data_daily['date'].dt.year

    weather_data_daily = weather_data_daily.rename(columns={'country_y':'country'}).drop(columns=['country_x','id'])

    weather_data_yearly = weather_data_daily.groupby(['year','country','region','continent'])[['avg_temp_c', 'min_temp_c', 'max_temp_c', 'precipitation_mm']].mean().reset_index()
    
    #limiting all data to only the one starting in 1970
    co2_emission = co2_emission[co2_emission['year']>=1970]
    co2_emission = co2_emission[['country', 'year', 'iso_code', 'population', 'gdp', 'co2', 'co2_growth_abs', 'co2_growth_prct']]

    #Excluding all the entries for which we don't have the iso_code right now
    co2_emission = co2_emission[~co2_emission.isin(co2_emission[co2_emission['iso_code'].isnull()]['country'].unique())]
    #deleting the NA rows for which no country information can be found
    co2_emission = co2_emission.dropna(subset='country')

    #drop the GDP column
    co2_emission = co2_emission.drop(columns='gdp')

    #merging the yearly data and CO2 Dataframe
    weather_data_yearly = weather_data_yearly.merge(co2_emission, how='left', on=['year','country']).sort_values(by=['country','year'])

    #Creating additional feature, calculating the difference between 2 consecutive years of the temperatures
    weather_data_yearly['max_temp_diff'] = weather_data_yearly.groupby('country')['max_temp_c'].diff().fillna(0, inplace=True)
    weather_data_yearly['min_temp_diff'] = weather_data_yearly.groupby('country')['min_temp_c'].diff().fillna(0, inplace=True)
    weather_data_yearly['avg_temp_diff'] = weather_data_yearly.groupby('country')['avg_temp_c'].diff().fillna(0, inplace=True)
    weather_data_yearly['population_diff'] = weather_data_yearly.groupby('country')['population'].diff().fillna(0, inplace=True)

    weather_data_yearly[['max_temp_diff','min_temp_diff','avg_temp_diff','population_diff']].fillna(0, inplace=True)
    
    return weather_data_yearly, weather_data_daily

def save_data(data1, data2, database_filename):
    """Aim to save the dataframe created within the SQL Database
    Args : 
    Data1 : the weather_data_yearly
    Data2 : the weather_data_daily
    database_filename : The name of the Database where the dataframe should be placed"""
    from sqlalchemy import create_engine
    #Create the enging for database connection
    engine = create_engine('sqlite:///{}'.format(database_filename))
    #save the first dataframe
    data1.to_sql('weather_data_yearly', engine, index=False, if_exists='replace')
    #save the second dataframe
    data2.to_sql('weather_data_daily', engine, index=False, if_exists='replace')

def main_start():
    """start of application for clean-up and saving data"""
    print('Collecting weather data')
    weather_data, countries, co2_emission, station_info = load_data()

    print('Cleaning and finalizing weather data')
    weather_data_yearly, weather_data_daily = clean_data(weather_data, countries, co2_emission, station_info)

    print('saving to database')
    save_data(weather_data_yearly, weather_data_daily, 'data\weather_data.db')

    print('All Weather Data are Ready')   

if __name__ == '__main_start__':
    main_start()

main_start()

