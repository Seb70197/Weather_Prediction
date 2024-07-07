# WEATHER PREDICTION, CLIMATE CHANGE IMPACT & THE ROLE OF THE HUMANITY ON THE WEATHER

- __Introduction__ :
Global Warming is a fact already proven by different scientist around the world ! The impact of the humanbeing on the climate is a fact !   
The raise of the temperatures are having for source different areas, immensily driven by the human activities on the planet and how the ressources are used and consumed.  
We will try within this app to raise awareness on the human impact on the global warming and try to project the weather situation in the future  
  
  
- __Goal__ :
Within this application, we will try to provide visualization on different features in order to raise awareness of the human impact on the global warming.
The application should contain :
    - A website enabling the use to see the evolution of different feature along a yearly axis.
    - The possibility for the user to wheither look at a country in specific of see the global information
    - Provide a projection of the weather according to user input on Year, CO2 Increase and Population difference (mostly increase)
    - Provide the user, once input is given, to show a prediction on the Average, Minimum and max temperature for the provided year.

<br>

- __Dataset Information__ :  
The Data used for this analysis and prediction are coming from 2 differents sources :  
    - Weather information as well as cities and countries are coming from a dataset available from Kaggle, gathered from a Kaggle User and coming from the [Meteostat.](https://meteostat.net/en/)  
    - CO2 emission as well as the energy data are coming from the database of [Our World in Data.](https://ourworldindata.org/)
    - We will limit the investigation and utilization of the data by starting with the year 1970 (decision taken out of the EDA and due to data presence)
<br>

- __Measures__ :
Within the application, I created a machine learning model based on RandomForestRegression to show the temperature evolution.

<br>

## INSTALLATION

Make sure all the necessary python package are installed within your machine.
Start with the console and run the run.py application. This should automatically start the webpage with the visualization.

## UTILIZATION

The WebPage contains following elements :
- A Visualization of the evolution of the temperatures, Average, Minimum and Maximum temperature
- A Visualization of the evolution of the CO2 emissions
- A Visualization of the population evolution

All within the period between 1970 to 2022.

The user is having the possibility to change the visualization according to a country of his/her choice. When the application starts, by default, the global information is displayed.

The bottom section, after the visualization, is providing the user the possibility to enter 3 features
- Year of his choice (e.g. 2023)
- The increase of C02 in Percent to be enter as a whole number (e.g. 2 --> Will be translated by the application to 2% and proceed with the calculation)
- Difference in population : Enter a whole number as an increase of population of the user's choice.

By Clicking on "Submit", once the selection is done, the user get a prediction of the 3 mains temperatures information, appearing only if the user enter some values.

## CONTENT OF THE APPLICATION 
- Data Folder : Contains the data used and data preparation for the machine learning model, it saves as well the cleaned data into a database present within the application.
- models Folder : Contains the machine learning model created from the data
- static : Contains the css file used for enriching the webapplication and creating stuning presentation :)
- templates : contains the HTML page rendered once the application is launched

The main folders contains as well :
- A jupyter Notebook where some analyze were done during the application creation
- the run.py file which should be use to start the program
- The weather_data.db created after data clean-up !
