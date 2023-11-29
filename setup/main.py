import pandas as pd
from datetime import date
from time import sleep
import os, traceback
import db, ses
import json
from getpass import getpass
import s3
import schedule

def execute(key):
    try:
        # Get DB connection objects
        postgres_conn = db.get_postgres_connection_object(key)
        mysql_conn = db.get_mysql_connection_object(key)

        # Retrieve data from DB tables
        with open(os.path.dirname(os.path.realpath(__file__))+'/config.json') as f:
            config = json.load(f)
        active_users = db.select_query(config['reports']['mt--reports']['postgres']['get_active_users'], postgres_conn)
        lcomp_data = db.select_query(config['reports']['mt--reports']['mysql']['get_lessons_completion'], mysql_conn)

        # Clean & filter required data
        data = process_data(active_users, lcomp_data)

        # Prepare CSV report named with today's prefix
        today = date.today() 
        today_str = today.strftime("%d_%m_%Y")
        file_name = f'{today_str}'+config['reports']['mt--reports']['s3']['file_name_suffix']
        data.to_csv(file_name, index=False)

        # Connect to S3 bucket & upload the CSV report
        s3.upload_to_s3(key, config['reports']['mt--reports']['s3']['bucket_name'], file_name)

        # Remove the CSV report locally
        os.remove(file_name)

    except Exception as e:
        print(e)
        ses.send_email(key, subject='ISSUE: Monthly Lessons Completion Report', message=traceback.format_exc())

def process_data(active_users, lcomp_data):
    with open(os.path.dirname(os.path.realpath(__file__))+'/config.json') as f:
        config = json.load(f)
    # Using pandas join the datasets with user_id and completion_date last 30 days condition
    df = active_users.merge(lcomp_data, on=config['reports']['mt--reports']['join']['id'])
    # Converting completion_date to datetime for filtering
    df[config['reports']['mt--reports']['condition']['id']] = pd.to_datetime(df[config['reports']['mt--reports']['condition']['id']])
    # Filtering for last 30 days
    df = df[df[config['reports']['mt--reports']['condition']['id']] >= (pd.Timestamp.now() - pd.Timedelta(config['reports']['mt--reports']['condition']['before'], config['reports']['mt--reports']['condition']['metric']))]
    # Group by user_id with completion_date & no of the lesson_ids
    df = df.groupby([config['reports']['mt--reports']['join']['id'], pd.Grouper(key=config['reports']['mt--reports']['condition']['id'], freq=config['reports']['mt--reports']['condition']['metric'])]).lesson_id.count().reset_index()
    # Group by user_id and take the count(*) using sum()
    df = df.groupby(config['reports']['mt--reports']['join']['id']).lesson_id.sum().reset_index()
    # Renaming column name
    df = df.rename(columns={'lesson_id': config['reports']['mt--reports']['aliases']['lesson_id']})
    return df

# Load Configuration file
with open(os.path.dirname(os.path.realpath(__file__))+'/config.json') as f:
        config = json.load(f)

def check_date(key):
    # Check if today is the Day 1 of the current month
    # If so, the report needs to be prepared & uploaded to a S3 bucket.
    if date.today().day == config['reports']['mt--reports']['scheduled_day_of_month']:
        execute(key)

if __name__ == "__main__":
    # On running the main script, it asks for decryption key to decrypt the env file values
    # The entering key in the command prompt won't be visible as the user types it
    key = getpass("Enter decryption key: ")
    # Scheduling an every day job at 10am to check if it is Day 1 of the month.
    schedule.every().day.at(config['reports']['mt--reports']['scheduled_time']).do(check_date, key)
    while True:
        schedule.run_pending()
        sleep(1)
