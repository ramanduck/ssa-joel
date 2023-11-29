import boto3
import os
from secure import decrypt
from dotenv import load_dotenv
import logger as log
import traceback

load_dotenv()

def send_email(key, subject, message):
    try: 

        AWS_SECRET_KEY = decrypt(os.environ.get("AWS_SECRET_KEY"), key)
        AWS_ACCESS_KEY = decrypt(os.environ.get("AWS_ACCESS_KEY"), key)
        AWS_REGION = decrypt(os.environ.get("AWS_REGION"), key)
        SES_SENDER_EMAIL = decrypt(os.environ.get("SES_SENDER_EMAIL"), key)
        RECEIPIENT_EMAILS = decrypt(os.environ.get("RECEIPIENT_EMAILS"), key)

        ses_client = boto3.client(
            "ses",
            region_name = AWS_REGION,
            aws_access_key_id = AWS_ACCESS_KEY,
            aws_secret_access_key = AWS_SECRET_KEY
        )

        ses_client.send_email(
            Destination={
                'ToAddresses': [
                    RECEIPIENT_EMAILS,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': message,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': subject,
                },
            },
            Source=SES_SENDER_EMAIL      
        )

    except Exception as e:
        print(e)
        log.logerror('AWS SES Service Failure')
        log.logerror(traceback.format_exc())
