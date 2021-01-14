# step 1 - import modules
import requests
import json
import os
from airflow import DAG
from datetime import datetime
from datetime import date
# Operators; we need this to operate!
from airflow.operators.python_operator import PythonOperator
import tweepy
import pandas as pd
from textblob import TextBlob
from datetime import datetime
from datetime import date

def get_sentiment_analysis(tweet):
    blob = TextBlob(tweet)
    return blob.sentiment.polarity

def extract_string_from_tweet(tweet):
    return tweet._json["full_text"]

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
    'Milestone3',
    default_args=default_args,
    description='Fetching Tweets and Performing sentiment analysis',
    schedule_interval='@daily',
)

# step 4 Define tasks
def store_data(**context):
    df = context['task_instance'].xcom_pull(task_ids='extract_data')
    df = df.set_index("date_of_interest")
    df.to_csv("data/nyccovid.csv")

def fetch_tweets(**context):
    
    key1="2lIEHEoY3v71FbOcqyrOOXpu0"
    key2="y0BOK3oEsCoDc0OTPW9jGEtluTldd4HkpgQllELHRE3UcW7TF6"
    key3="294213322-Wv37AhbUnkPmISZUnNBHdmT2MJMhoDmRosOihywQ"
    key4="fht2F9rc1NoM4rO3mv2uE85G8Cp9csGidGfAu9FXs3u87"
    auth = tweepy.OAuthHandler(key1,key2)
    auth.set_access_token(key3, key4)
    
    api = tweepy.API(auth)

    canada_geo_id = api.geo_search(query="Canada", granularity="country")[0].id
    rwanda_geo_id = api.geo_search(
        query="Rwanda", granularity="country")[0].id
    canada = list(tweepy.Cursor(api.search, q='place:%s' % canada_geo_id,
                                lang='en', result_type='recent', count=20, tweet_mode="extended").items(20))
    rwanda = list(tweepy.Cursor(api.search, q='place:%s' % rwanda_geo_id,
                                lang='en', result_type='recent', count=20, tweet_mode="extended").items(20))
    canada = list(
        map(extract_string_from_tweet, canada))
    rwanda = list(
        map(extract_string_from_tweet, rwanda))
    tweets = {"canada": canada, "rwanda": rwanda,"timestamps":[datetime.now().strftime("%Y-%m-%d %H:%M:%S")]}

    return tweets

def analyze_sentiments(**context):
    tweets=context['task_instance'].xcom_pull(task_ids='fetch_tweets')
    tweets["canada"]=list(
    map(get_sentiment_analysis, tweets["canada"]))

    tweets["rwanda"]=list(
        map(get_sentiment_analysis, tweets["rwanda"]))
    return tweets




def load_old_tweets(**context):
    old_tweets=None
    tweets=context['task_instance'].xcom_pull(task_ids='analyze_sentiments')
    try:
        with open('oldTweetSentiments.json', 'r') as f:
            old_tweets=json.load(f)
            old_tweets["canada"]+=tweets["canada"]
            old_tweets["rwanda"]+=tweets["rwanda"]
            old_tweets["timestamps"].append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except FileNotFoundError:
        old_tweets=tweets

    with open('oldTweetSentiments.json', 'w') as f:
            json.dump(old_tweets, f)
    return old_tweets

def calculate_average_sentiments(**context):
    old_tweets=context['task_instance'].xcom_pull(task_ids='load_old_tweets')
    rwanda_score=sum(old_tweets["rwanda"])/len(old_tweets["rwanda"])
    canada_score=sum(old_tweets["canada"])/len(old_tweets["canada"])

t1 = PythonOperator(
    task_id='fetch_tweets',
    provide_context=True,
    python_callable=fetch_tweets,
    dag=dag,
)

t2 = PythonOperator(
    task_id='analyze_sentiments',
    provide_context=True,
    python_callable=analyze_sentiments,
    dag=dag,
)
t3 = PythonOperator(
    task_id='load_old_tweets',
    provide_context=True,
    python_callable=load_old_tweets,
    dag=dag,
)
t4 = PythonOperator(
    task_id='calculate_average_sentiments',
    provide_context=True,
    python_callable=calculate_average_sentiments,
    dag=dag,
)
t1>>t2>>t3>>t4
