import boto3
from secure import decrypt
import os, traceback
from dotenv import load_dotenv
import ses
import logger as log

load_dotenv()

def upload_to_s3(key, bucket_name, file_name):

    try:
        AWS_SECRET_KEY = decrypt(os.environ.get("AWS_SECRET_KEY"), key)
        AWS_ACCESS_KEY = decrypt(os.environ.get("AWS_ACCESS_KEY"), key)
        s3_conn_obj = boto3.client('s3',
                        aws_access_key_id = AWS_ACCESS_KEY,
                        aws_secret_access_key = AWS_SECRET_KEY
                        )
        return s3_conn_obj.upload_file( file_name, bucket_name, file_name )
    
    except Exception as e:
        print(e)
        log.logerror('AWS S3 Connectivity/File Upload Error')
        log.logerror(traceback.format_exc())
        ses.send_email(key, subject='AWS S3 Connectivity/File Upload Error', message=traceback.format_exc())