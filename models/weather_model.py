import sys
import pandas as pd
from sqlalchemy import create_engine
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor 
from sklearn.metrics import classification_report
import warnings

warnings.filterwarnings('ignore')

def load_data(database_filepath):
    """Load data from the database and create dataframe containing the weather, countries, co2 and station information
    
    Args:
    database_filepath : Database where the data are saved
        
    Return : 3 dataframe X for the messages to predict, Y for their target labels and categories containing the labels names"""

    engine = create_engine('sqlite:///{}'.format(database_filepath))
    #read the data from the database and create the relevant dataframe
    df = pd.read_sql_query('SELECT * FROM weather_data_yearly', engine)
    
    x= df[['year','co2','population_diff']]
    y= df[['avg_temp_c','min_temp_c','max_temp_c']]
    

    return x, y

def model_pipeline():
    """create the machine learning pipeline containing different parameters for RandomForest
    
    Return : The model used within the WebApplication"""

    pipeline = Pipeline([('clf', RandomForestRegressor(random_state=0))
                 ])

    #pipeline parameters to apply to model
    parameters = {
        'clf__max_features':[1,2],
        'clf__n_estimators':[100,150,200,250,300],
        'clf__n_jobs':[1,5,10,15,20,25]
    }

    #take best parameters for our model
    model = GridSearchCV(pipeline, parameters)
    
    return model

def save_model(model):
    """Save model within a pickle file for utilization within the WebApplication"""
    import pickle as pk
    #Define model pipeline name
    filename = 'models/weather_model.pkl'
    #Update model
    pk.dump(model, open(filename, 'wb'))


def main():
        
    x, y = load_data('data\weather_data.db')
    x['co2'].fillna(0,inplace=True)    
    X_train, X_test, y_train, y_test = train_test_split(x, y, random_state=0, test_size=0.2)

    print('Building Model')
    model = model_pipeline()

    print('Training model')
    model.fit(X_train, y_train)

    print('Evaluating Model')
    score = model.score(X_test, y_test)

    print('Saving model')
    save_model(model)

    print('Trained model saved')

if __name__ == '__main__':
    main()

main()