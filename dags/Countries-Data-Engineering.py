# step 1 - import modules
import requests
import json

from airflow import DAG
from datetime import datetime
from datetime import date
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import numpy as np
from matplotlib import pyplot
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn import preprocessing
import warnings
import os
from sklearn.impute import SimpleImputer
from scipy.stats.mstats import winsorize
import scipy.stats as stats

# step 2 - define default args
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 12, 13)
    }


# step 3 - instantiate DAG
dag = DAG(
    'Countries-Data-Engineering',
    default_args=default_args,
    description='Merging of three datasets of Data Engineering project',
    schedule_interval='@once',
)

# step 4 Define tasks
def store_data(**context):
    df = context['task_instance'].xcom_pull(task_ids='extract_data')
    df = df.set_index("date_of_interest")
    df.to_csv("data/nyccovid.csv")


def extract_happiness_report(**kwargs):
    world_happiness_report_dict={}
    # Populating the dictionary
    for i in range (5,10):
        world_happiness_report_dict["201"+str(i)]=pd.read_csv("https://raw.githubusercontent.com/Alsouidan/shared-data-CSEN-1095/main/"+"201"+str(i)+".csv")
    return world_happiness_report_dict
def happiness_report_cleaning_and_tidying_and_tranforming(**context):
    world_happiness_report_dict = context['task_instance'].xcom_pull(task_ids='extract_happiness_report')

    # Renaming Columns
    
    world_happiness_report_dict["2015"]=world_happiness_report_dict["2015"].rename(columns={"Economy (GDP per Capita)":"GDP per Capita",
                                                    "Family":"Social Support",
                                                    "Health (Life Expectancy)":"Life Expectancy",
                                                    "Trust (Government Corruption)":"Government Corruption",
                                                    })
    world_happiness_report_dict["2016"]=world_happiness_report_dict["2016"].rename(columns={"Economy (GDP per Capita)":"GDP per Capita",
                                                    "Family":"Social Support",
                                                    "Health (Life Expectancy)":"Life Expectancy",
                                                    "Trust (Government Corruption)":"Government Corruption",
                                                    })
    world_happiness_report_dict["2017"]=world_happiness_report_dict["2017"].rename(columns={"Happiness.Rank":"Happiness Rank",
                                                                                        "Happiness.Score":"Happiness Score",
                                                                                        "Whisker.high":"Lower Confidence Interval",
                                                                                        "Whisker.low":"Upper Confidence Interval",
                                                                                        "Economy..GDP.per.Capita.":"GDP per Capita",
                                                                                        "Family":"Social Support",
                                                                                        "Health..Life.Expectancy.":"Life Expectancy",
                                                                                        "Trust..Government.Corruption.":"Government Corruption",
                                                                                        "Dystopia.Residual":"Dystopia Residual"
                                                                                        })

    world_happiness_report_dict["2018"]=world_happiness_report_dict["2018"].rename(columns={
    "Overall rank":"Happiness Rank",
    "Country or region":"Country",
    "Score":"Happiness Score",
    "GDP per capita":"GDP per Capita",
    "Social support":"Social Support",
    "Healthy life expectancy":"Life Expectancy",
    "Freedom to make life choices":"Freedom",
    "Perceptions of corruption":"Government Corruption"
    })
    world_happiness_report_dict["2019"]=world_happiness_report_dict["2019"].rename(columns={
   "Overall rank":"Happiness Rank",
    "Country or region":"Country",
    "Score":"Happiness Score",
    "GDP per capita":"GDP per Capita",
    "Social support":"Social Support",
    "Healthy life expectancy":"Life Expectancy",
    "Freedom to make life choices":"Freedom",
    "Perceptions of corruption":"Government Corruption"
    })
    countries_regions_dict={}
    for index,row in world_happiness_report_dict["2015"].iterrows():
        countries_regions_dict[row["Country"]]=row["Region"]
    for index,row in world_happiness_report_dict["2016"].iterrows():
        countries_regions_dict[row["Country"]]=row["Region"]
    # Adding region columns
    world_happiness_report_dict["2017"]["Region"]=world_happiness_report_dict["2017"]["Country"].map(countries_regions_dict)
    world_happiness_report_dict["2018"]["Region"]=world_happiness_report_dict["2018"]["Country"].map(countries_regions_dict)
    world_happiness_report_dict["2019"]["Region"]=world_happiness_report_dict["2019"]["Country"].map(countries_regions_dict)
    # dropping odd column
    world_happiness_report_dict["2016"]=world_happiness_report_dict["2016"].drop(["Dystopia Residual","Lower Confidence Interval","Upper Confidence Interval"],axis=1)
    world_happiness_report_dict["2017"]=world_happiness_report_dict["2017"].drop(["Dystopia Residual","Lower Confidence Interval","Upper Confidence Interval"],axis=1)
    world_happiness_report_dict["2015"]=world_happiness_report_dict["2015"].drop(["Dystopia Residual","Standard Error"],axis=1)
    # Sorting columns
    for i in range (5,10):
        world_happiness_report_dict["201"+str(i)]=world_happiness_report_dict["201"+str(i)].reindex(sorted(world_happiness_report_dict["201"+str(i)].columns), axis=1)
    # merging dfs
    dataframes_to_be_merged=[]
    for i in range (5,10):
        world_happiness_report_dict["201"+str(i)]["Year"]="201"+str(i)
        dataframes_to_be_merged.append(world_happiness_report_dict["201"+str(i)])
    world_happiness_report_df=pd.concat(dataframes_to_be_merged)
    # Removing Nulls values
    world_happiness_report_df=world_happiness_report_df[world_happiness_report_df["Government Corruption"].notna()]
    world_happiness_report_df=world_happiness_report_df[world_happiness_report_df["Region"].notna()]
    # Normalize columns
    z_scaler = StandardScaler()
    col_array=["Freedom","GDP per Capita","Generosity","Government Corruption","Happiness Score","Life Expectancy","Social Support"]
    min_max_scaler = MinMaxScaler()
    world_happiness_report_df[col_array] = min_max_scaler.fit_transform(world_happiness_report_df[col_array])
    world_happiness_report_df_means=world_happiness_report_df.groupby(['Region',"Year"]).mean()
    col_array=["Freedom","GDP per Capita","Generosity","Government Corruption","Happiness Score","Life Expectancy","Social Support"]
    # Renaming columns 
    world_happiness_report_df=world_happiness_report_df.rename(columns={"Freedom":"Freedom on Happiness",
                                         "GDP per Capita":"GDP per Capita on Happiness",
                                         "Generosity":"Generosity on Happiness",
                                         "Government Corruption":"Government Corruption on Happiness",
                                         "Life Expectancy":"Life Expectancy on Happiness",
                                         "Social Support":"Social Support on Happiness"
                                         })
    return world_happiness_report_df,countries_regions_dict
def extract_life_expectancy(**context): 
    # reading the csv
    Life_Expectancy_Data_df = pd.read_csv('https://raw.githubusercontent.com/Alsouidan/shared-data-CSEN-1095/main/Life%20Expectancy%20Data.csv')
    # renaming the columns
    Life_Expectancy_Data_df.columns = ['Country','Year','Status','Life Expectancy','Adult Mortality','Infant Deaths',
    'Alcohol','Percentage Expenditure','Hepatitis B','Measles','BMI','Under-Five Deaths','Polio','Total Expenditure',
    'Diphtheria','HIV/AIDS','GDP','Population','Thinness 1-19 Years','Thinness 5-9 Years',
    'Income Composition of Resources','Schooling']
    return Life_Expectancy_Data_df
def life_expectancy_cleaning_and_tidying_and_transforming(**context):
    Life_Expectancy_Data_df = context['task_instance'].xcom_pull(task_ids='extract_life_expectancy')

    fill_list = ['Country', 'Year', 'Status', 'Life Expectancy', 'Adult Mortality',
       'Infant Deaths', 'Alcohol', 'Percentage Expenditure', 'Hepatitis B',
       'Measles', 'BMI', 'Under-Five Deaths', 'Polio', 'Total Expenditure',
       'Diphtheria', 'HIV/AIDS', 'GDP', 'Population',
       'Thinness 1-19 Years', 'Thinness 5-9 Years',
       'Income Composition of Resources', 'Schooling']

    filter_list = ['Life Expectancy', 'Adult Mortality',
       'Infant Deaths', 'Alcohol', 'Percentage Expenditure', 'Hepatitis B',
       'Measles', 'BMI', 'Under-Five Deaths', 'Polio', 'Total Expenditure',
       'Diphtheria', 'HIV/AIDS', 'GDP', 'Population',
       'Thinness 1-19 Years', 'Thinness 5-9 Years',
       'Income Composition of Resources', 'Schooling']
    # filling the null values with interpolate 
    country_list = Life_Expectancy_Data_df.Country.unique()
    for country in country_list:
        Life_Expectancy_Data_df.loc[Life_Expectancy_Data_df['Country'] == country,fill_list] = Life_Expectancy_Data_df.loc[Life_Expectancy_Data_df['Country'] == country,fill_list].interpolate()
    #Life_Expectancy_Data_df.dropna(inplace=True)
    # filling null values with mode
    for name in filter_list: 
        Life_Expectancy_Data_df[name].fillna(Life_Expectancy_Data_df[name].mode().iloc[0], inplace=True)
    # Remove outliers using winsorization
    winsorized_Life_Expectancy = winsorize(Life_Expectancy_Data_df['Life Expectancy'],(0.01,0))
    winsorized_Adult_Mortality = winsorize(Life_Expectancy_Data_df['Adult Mortality'],(0,0.03))
    winsorized_Infant_Deaths = winsorize(Life_Expectancy_Data_df['Infant Deaths'],(0,0.11))
    winsorized_Alcohol = winsorize(Life_Expectancy_Data_df['Alcohol'],(0,0.01))
    winsorized_Percentage_Exp = winsorize(Life_Expectancy_Data_df['Percentage Expenditure'],(0,0.135))
    winsorized_HepatitisB = winsorize(Life_Expectancy_Data_df['Hepatitis B'],(0.11,0))
    winsorized_Measles = winsorize(Life_Expectancy_Data_df['Measles'],(0,0.19))
    winsorized_Under_Five_Deaths = winsorize(Life_Expectancy_Data_df['Under-Five Deaths'],(0,0.14))
    winsorized_Polio = winsorize(Life_Expectancy_Data_df['Polio'],(0.1,0))
    winsorized_Tot_Exp = winsorize(Life_Expectancy_Data_df['Total Expenditure'],(0,0.02))
    winsorized_Diphtheria = winsorize(Life_Expectancy_Data_df['Diphtheria'],(0.11,0))
    winsorized_HIV = winsorize(Life_Expectancy_Data_df['HIV/AIDS'],(0,0.19))
    winsorized_GDP = winsorize(Life_Expectancy_Data_df['GDP'],(0,0.15))
    winsorized_Population = winsorize(Life_Expectancy_Data_df['Population'],(0,0.15))
    winsorized_thinness_1to19_years = winsorize(Life_Expectancy_Data_df['Thinness 1-19 Years'],(0,0.04))
    winsorized_thinness_5to9_years = winsorize(Life_Expectancy_Data_df['Thinness 5-9 Years'],(0,0.04))
    winsorized_Income_Comp_Of_Resources = winsorize(Life_Expectancy_Data_df['Income Composition of Resources'],(0.1,0))
    winsorized_Schooling = winsorize(Life_Expectancy_Data_df['Schooling'],(0.025,0.01))
    winsorized_list = [winsorized_Life_Expectancy,winsorized_Adult_Mortality,winsorized_Alcohol,
    winsorized_Measles,winsorized_Infant_Deaths, winsorized_Percentage_Exp, winsorized_HepatitisB,
    winsorized_Under_Five_Deaths, winsorized_Polio, winsorized_Tot_Exp, winsorized_Diphtheria,
    winsorized_HIV, winsorized_GDP, winsorized_Population, winsorized_thinness_1to19_years,
    winsorized_thinness_5to9_years, winsorized_Income_Comp_Of_Resources, winsorized_Schooling]
    
    name_list = ["winsorized_Life_Expectancy","winsorized_Adult_Mortality","winsorized_Alcohol",
    "winsorized_Measles","winsorized_Infant_Deaths", "winsorized_Percentage_Exp", "winsorized_HepatitisB",
    "winsorized_Under_Five_Deaths", "winsorized_Polio", "winsorized_Tot_Exp", "winsorized_Diphtheria",
    "winsorized_HIV", "winsorized_GDP", "winsorized_Population", "winsorized_thinness_1to19_years",
    "winsorized_thinness_5to9_years", "winsorized_Income_Comp_Of_Resources", "winsorized_Schooling"]

    Life_Expectancy_Data_df['winsorized_Life_Expectancy'] = winsorized_Life_Expectancy
    Life_Expectancy_Data_df['winsorized_Adult_Mortality'] = winsorized_Adult_Mortality
    Life_Expectancy_Data_df['winsorized_Infant_Deaths'] = winsorized_Infant_Deaths
    Life_Expectancy_Data_df['winsorized_Alcohol'] = winsorized_Alcohol
    Life_Expectancy_Data_df['winsorized_Percentage_Exp'] = winsorized_Percentage_Exp
    Life_Expectancy_Data_df['winsorized_HepatitisB'] = winsorized_HepatitisB
    Life_Expectancy_Data_df['winsorized_Under_Five_Deaths'] = winsorized_Under_Five_Deaths
    Life_Expectancy_Data_df['winsorized_Polio'] = winsorized_Polio
    Life_Expectancy_Data_df['winsorized_Tot_Exp'] = winsorized_Tot_Exp
    Life_Expectancy_Data_df['winsorized_Diphtheria'] = winsorized_Diphtheria
    Life_Expectancy_Data_df['winsorized_HIV'] = winsorized_HIV
    Life_Expectancy_Data_df['winsorized_GDP'] = winsorized_GDP
    Life_Expectancy_Data_df['winsorized_Population'] = winsorized_Population
    Life_Expectancy_Data_df['winsorized_thinness_1to19_years'] = winsorized_thinness_1to19_years
    Life_Expectancy_Data_df['winsorized_thinness_5to9_years'] = winsorized_thinness_5to9_years
    Life_Expectancy_Data_df['winsorized_Income_Comp_Of_Resources'] = winsorized_Income_Comp_Of_Resources
    Life_Expectancy_Data_df['winsorized_Schooling'] = winsorized_Schooling
    Life_Expectancy_Data_df['winsorized_Measles'] = winsorized_Measles
    Life_Expectancy_Data_df['Life Expectancy'] = winsorized_Life_Expectancy
    Life_Expectancy_Data_df['Adult Mortality'] = winsorized_Adult_Mortality
    Life_Expectancy_Data_df['Infant Deaths'] = winsorized_Infant_Deaths
    Life_Expectancy_Data_df['Alcohol'] = winsorized_Alcohol
    Life_Expectancy_Data_df['Percentage Expenditure'] = winsorized_Percentage_Exp
    Life_Expectancy_Data_df['HepatitisB'] = winsorized_HepatitisB
    Life_Expectancy_Data_df['Under Five Deaths'] = winsorized_Under_Five_Deaths
    Life_Expectancy_Data_df['Polio'] = winsorized_Polio
    Life_Expectancy_Data_df['Total Expenditure'] = winsorized_Tot_Exp
    Life_Expectancy_Data_df['Diphtheria'] = winsorized_Diphtheria
    Life_Expectancy_Data_df['HIV/AIDS'] = winsorized_HIV
    Life_Expectancy_Data_df['GDP'] = winsorized_GDP
    Life_Expectancy_Data_df['Population'] = winsorized_Population
    Life_Expectancy_Data_df['Thinness 1-19 Years'] = winsorized_thinness_1to19_years
    Life_Expectancy_Data_df['Thinness 5-9 Years'] = winsorized_thinness_5to9_years
    Life_Expectancy_Data_df['Income Composition of Resources'] = winsorized_Income_Comp_Of_Resources
    Life_Expectancy_Data_df['Schooling'] = winsorized_Schooling
    Life_Expectancy_Data_df['Measles'] = winsorized_Measles
    Life_Expectancy_Data_df=Life_Expectancy_Data_df.drop(['winsorized_Life_Expectancy', 'winsorized_Adult_Mortality',
        'winsorized_Infant_Deaths', 'winsorized_Alcohol',
        'winsorized_Percentage_Exp', 'winsorized_HepatitisB',
        'winsorized_Under_Five_Deaths', 'winsorized_Polio',
        'winsorized_Tot_Exp', 'winsorized_Diphtheria', 'winsorized_HIV',
        'winsorized_GDP', 'winsorized_Population',
        'winsorized_thinness_1to19_years',
        'winsorized_thinness_5to9_years',
        'winsorized_Income_Comp_Of_Resources', 'winsorized_Schooling',
        'winsorized_Measles'],axis=1)
    return Life_Expectancy_Data_df
def extract_250_countries(**context):
    df_250_countries = pd.read_csv("https://raw.githubusercontent.com/Alsouidan/shared-data-CSEN-1095/main/250%20Country%20Data.csv",index_col=0)
    return df_250_countries
def countries_250_cleaning_and_tidying_and_transforming(**context):
    df_250_countries = context['task_instance'].xcom_pull(task_ids='extract_250_countries')

    # ensuring the correct format of float numbers
    df_250_countries['Real Growth Rating(%)'] = df_250_countries['Real Growth Rating(%)'].str.extract('(\d*\.\d+|\d+)', expand=False).astype(float)
    df_250_countries['Literacy Rate(%)'] = df_250_countries['Literacy Rate(%)'].str.extract('(\d*\.\d+|\d+)', expand=False).astype(float)
    df_250_countries['Inflation(%)'] = df_250_countries['Inflation(%)'].str.extract('(\d*\.\d+|\d+)', expand=False).astype(float)
    df_250_countries['Unemployement(%)'] = df_250_countries['Unemployement(%)'].str.extract('(\d*\.\d+|\d+)', expand=False).astype(float)
    # Dropping null values of region column
    df_250_countries[df_250_countries['region'].notna()]
    # aggregating by region to fill null values per region
    regions_df = df_250_countries.groupby('region')
    asia_region = regions_df.get_group('Asia')
    europe_region = regions_df.get_group('Europe')
    africa_region = regions_df.get_group('Africa')
    oceania_region = regions_df.get_group('Oceania')
    americas_region = regions_df.get_group('Americas')
    polar_region = regions_df.get_group('Polar')
    asia_region.fillna({'gini':asia_region['gini'].mode().iloc[1]}, inplace = True)
    asia_region.fillna({'Real Growth Rating(%)':asia_region['Real Growth Rating(%)'].mode().iloc[0]}, inplace=True)
    asia_region.fillna({'Literacy Rate(%)':asia_region['Literacy Rate(%)'].mode().iloc[0]}, inplace = True)
    asia_region.fillna({'area': 0}, inplace=True)
    europe_region.fillna({'gini':europe_region['gini'].mean()}, inplace = True)
    europe_region.fillna({'Real Growth Rating(%)':europe_region['Real Growth Rating(%)'].mode().iloc[0]}, inplace = True)
    europe_region.fillna({'Literacy Rate(%)':europe_region['Literacy Rate(%)'].mode().iloc[0]}, inplace = True)
    europe_region.fillna({'Inflation(%)':europe_region['Inflation(%)'].mode().iloc[0]}, inplace = True)
    europe_region.fillna({'Unemployement(%)':europe_region['Unemployement(%)'].mean()}, inplace = True)
    europe_region.fillna({'area':0}, inplace = True)
    africa_region.fillna({'gini':africa_region['gini'].mode().iloc[1]}, inplace = True)
    africa_region.fillna({'Real Growth Rating(%)':africa_region['Real Growth Rating(%)'].mean()}, inplace = True)
    africa_region.fillna({'Literacy Rate(%)':africa_region['Literacy Rate(%)'].mode().iloc[0]}, inplace = True)
    africa_region.fillna({'Inflation(%)':africa_region['Inflation(%)'].mode().iloc[1]}, inplace = True)
    africa_region.fillna({'Unemployement(%)':africa_region['Unemployement(%)'].mode().iloc[0]}, inplace = True)
    africa_region.fillna({'area':0}, inplace = True)
    oceania_region.fillna({'gini':oceania_region['gini'].mean()}, inplace = True)
    oceania_region.fillna({'Real Growth Rating(%)':oceania_region['Real Growth Rating(%)'].mean()}, inplace = True)
    oceania_region.fillna({'Literacy Rate(%)':oceania_region['Literacy Rate(%)'].mode().iloc[0]}, inplace = True)
    oceania_region.fillna({'Inflation(%)':oceania_region['Inflation(%)'].mode().iloc[0]}, inplace = True)
    oceania_region.fillna({'Unemployement(%)':oceania_region['Unemployement(%)'].mode().iloc[0]}, inplace = True)
    americas_region.fillna({'gini':americas_region['gini'].mean()}, inplace = True)
    americas_region.fillna({'Real Growth Rating(%)':americas_region['Real Growth Rating(%)'].mode().iloc[0]}, inplace = True)
    americas_region.fillna({'Literacy Rate(%)':americas_region['Literacy Rate(%)'].mode().iloc[0]}, inplace = True)
    americas_region.fillna({'Inflation(%)':americas_region['Inflation(%)'].mode().iloc[0]}, inplace = True)
    americas_region.fillna({'Unemployement(%)':americas_region['Unemployement(%)'].mode().iloc[1]}, inplace = True)
    americas_region.fillna({'area':0}, inplace = True)
    # Remove outliers by winsorization
    col_dict = {'population':1 , 'area':2 ,
        'gini':3 , 'Real Growth Rating(%)': 4, 'Literacy Rate(%)': 5,
       'Inflation(%)' : 6, 'Unemployement(%)': 7}
    for variable,i in col_dict.items():
        winsorized_variable = winsorize(asia_region[variable],(0.2,0.1))
        winsorized_variable = winsorize(europe_region[variable],(0.05,0.2))
        winsorized_variable = winsorize(africa_region[variable],(0.2,0.1))
        winsorized_variable = winsorize(oceania_region[variable],(0.15,0.15))
        winsorized_variable = winsorize(americas_region[variable],(0.1,0.15))
    dataframe_set = [asia_region, europe_region, africa_region, oceania_region, americas_region]
    # merging back the regions
    tidy_250_countries = pd.concat(dataframe_set)
    tidy_250_countries=tidy_250_countries.drop(["region","subregion"],axis=1)
    # Renaming the columns 
    tidy_250_countries=tidy_250_countries.rename(columns={"name":"Country","population":"Population","area":"Area"})
    return tidy_250_countries
def merging_dataframes(**context):
    world_happiness_report_df,countries_regions_dict = context['task_instance'].xcom_pull(task_ids='happiness_report_cleaning_and_tidying_and_tranforming')
    Life_Expectancy_Data_df = context['task_instance'].xcom_pull(task_ids='life_expectancy_cleaning_and_tidying_and_transforming')
    tidy_250_countries = context['task_instance'].xcom_pull(task_ids='countries_250_cleaning_and_tidying_and_transforming')

    # Merging the three datasets based on the country names
    # Aggregating the years of the world happiness report and getting the mean
    world_happiness_report_agg=world_happiness_report_df.groupby("Country").mean()
    world_happiness_report_agg=world_happiness_report_agg.reset_index()
    world_happiness_report_agg["Region"]=world_happiness_report_agg["Country"].map(countries_regions_dict)
    Life_Expectancy_Data_df_agg=Life_Expectancy_Data_df.groupby(["Country","Status"]).mean()
    Life_Expectancy_Data_df_agg=Life_Expectancy_Data_df_agg.drop(["Year","Population"],axis=1)
    Life_Expectancy_Data_df_agg=Life_Expectancy_Data_df_agg.reset_index()
    merged_df=pd.merge(Life_Expectancy_Data_df_agg, world_happiness_report_agg, on='Country')
    merged_df=pd.merge(merged_df,tidy_250_countries, on="Country")
    return merged_df
def feature_engineering(**context):
    merged_df = context['task_instance'].xcom_pull(task_ids='merging_dataframes')

    #Feature 1 One hot encoding of status column
    # Get one hot encoding of columns B
    one_hot = pd.get_dummies(merged_df['Status'])
    # Drop column B as it is now encoded
    merged_df = merged_df.drop('Status',axis = 1)
    merged_df=merged_df.drop(["HepatitisB","Under-Five Deaths"],axis=1)
    # Join the encoded df
    merged_df = merged_df.join(one_hot)
    # Feature 2: Label Encode the Region column
    label_encoder = preprocessing.LabelEncoder() 
    merged_df['Region']= label_encoder.fit_transform(merged_df['Region'])
    keys = label_encoder.classes_
    values = label_encoder.transform(label_encoder.classes_)
    region_dictionary = dict(zip(keys, values))
    # Feature 3 :  Discretization of the happiness score column
    happiness_status = pd.cut(merged_df["Happiness Score"], [0,0.25,0.5,0.75,1],labels=["Very Sad",'Mildly Sad','Mildly Happy','Very Happy'])
    merged_df["Happiness Status"] = happiness_status
    label_encoder = preprocessing.LabelEncoder() 
    merged_df['Happiness Status']= label_encoder.fit_transform(merged_df['Happiness Status'])
    keys = label_encoder.classes_
    values = label_encoder.transform(label_encoder.classes_)
    happiness_status_dictionary = dict(zip(keys, values))
    # Feature 4 : Total Immnuization column (Interaction Feature)
    merged_df["Total Immunized Disease(%)"] = (merged_df["Hepatitis B"]+merged_df["Polio"]+merged_df["Diphtheria"])/3
    return merged_df
def store_as_csv(**context):
    merged_df = context['task_instance'].xcom_pull(task_ids='feature_engineering')
    merged_df.to_csv("Final_Data.csv")
t1 = PythonOperator(
    task_id='extract_happiness_report',
    provide_context=True,
    python_callable=extract_happiness_report,
    dag=dag,
)

t2 = PythonOperator(
    task_id='happiness_report_cleaning_and_tidying_and_tranforming',
    provide_context=True,
    python_callable=happiness_report_cleaning_and_tidying_and_tranforming,
    dag=dag,
)

t3= PythonOperator(
    task_id='extract_life_expectancy',
    provide_context=True,
    python_callable=extract_life_expectancy,
    dag=dag,
)
t4= PythonOperator(
    task_id='life_expectancy_cleaning_and_tidying_and_transforming',
    provide_context=True,
    python_callable=life_expectancy_cleaning_and_tidying_and_transforming,
    dag=dag,
    )
t5= PythonOperator(
    task_id='extract_250_countries',
    provide_context=True,
    python_callable=extract_250_countries,
    dag=dag,
)
t6= PythonOperator(
    task_id='countries_250_cleaning_and_tidying_and_transforming',
    provide_context=True,
    python_callable=countries_250_cleaning_and_tidying_and_transforming,
    dag=dag,
)

t7= PythonOperator(
    task_id='merging_dataframes',
    provide_context=True,
    python_callable=merging_dataframes,
    dag=dag,
)

t8= PythonOperator(
    task_id='feature_engineering',
    provide_context=True,
    python_callable=feature_engineering,
    dag=dag,
)
t9= PythonOperator(task_id='store_as_csv',
    provide_context=True,
    python_callable=store_as_csv,
    dag=dag,)
# step 5 - define dependencies
t1 >> t2 
t3 >> t4 
t5 >> t6 
[t2,t4,t6] >> t7 >> t8 >> t9
