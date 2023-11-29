from dotenv import load_dotenv
from secure import decrypt
import os
import psycopg2 as pg
import mysql.connector as mysql
import pandas as pd
import traceback
import ses

load_dotenv()

def get_postgres_connection_object(key):
    try:
        PG_CONN_HOST = decrypt(os.environ.get("POSTGRES_HOST"), key)
        PG_CONN_DB = decrypt(os.environ.get("POSTGRES_DB"), key)
        PG_CONN_USER = decrypt(os.environ.get("POSTGRES_USER"), key)
        PG_CONN_PWD = decrypt(os.environ.get("POSTGRES_PASSWORD"), key)
        pg_conn = pg.connect(
            host=PG_CONN_HOST,
            database=PG_CONN_DB,
            user=PG_CONN_USER,
            password=PG_CONN_PWD
        )
        return pg_conn

    except Exception as e:
        print(e)
        ses.send_email(key, subject='Postgres DB Connectivity Error', message=traceback.format_exc())

def get_mysql_connection_object(key):
    try:
        MYSQL_CONN_HOST = decrypt(os.environ.get("MYSQL_HOST"), key)
        MYSQL_CONN_DB = decrypt(os.environ.get("MYSQL_DB"), key)
        MYSQL_CONN_USER = decrypt(os.environ.get("MYSQL_USER"), key)
        MYSQL_CONN_PWD = decrypt(os.environ.get("MYSQL_PASSWORD"), key)
        mysql_conn = mysql.connect(
            host=MYSQL_CONN_HOST,
            database=MYSQL_CONN_DB,
            user=MYSQL_CONN_USER,
            password=MYSQL_CONN_PWD
        )
        return mysql_conn

    except Exception as e:
        print(e)
        ses.send_email(key, subject='MYSQL DB Connectivity Error', message=traceback.format_exc())

def select_query(query, database_connection_object):
    return pd.read_sql(query, con=database_connection_object)