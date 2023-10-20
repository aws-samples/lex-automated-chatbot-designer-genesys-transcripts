import argparse
import datetime
import json
import random
import sys
import uuid
import os
import boto3
import urllib.parse

s3 = boto3.client('s3')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    
    targetbucketname = os.environ["targetbucketname"]
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        convert(bucket, key, targetbucketname)
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

    

def get_random_time():
    TIME_STRING_FORMAT = '%02d:%02d:%02d'
    # Generate random number scaled to number of seconds in a day: (24*60*60) = 86,400
    time = int(random.random() * 86400)
    hours = int(time / 3600)
    minutes = int((time - hours * 3600) / 60)
    seconds = time - hours * 3600 - minutes * 60
    return TIME_STRING_FORMAT % (hours, minutes, seconds)

def convert_to_chatbot_format(genesys_json):
    print('you made it here!')
    cur_json = dict()
    cur_json['ContentMetadata'] = {}
    cur_json['ContentMetadata']['RedactionType'] = None
    cur_json['ContentMetadata']['Output'] = 'Raw'
    cur_json['CustomerMetadata'] = dict()
    cur_str = str(int(random.random() * 10000))
    cur_uuid = uuid.uuid4()
    cur_json['CustomerMetadata']['ContactId'] = '{}-{}'.format(cur_str, cur_uuid)
    cur_json['Participants'] = list()

    for index in range(len(genesys_json['participants'])):
        if genesys_json['participants'][index]['participantPurpose'] == 'ivr':
            cur_json['Participants'].append(
                {'ParticipantId': 'Agent',
                'ParticipantRole': 'AGENT'})  
        else:
            cur_json['Participants'].append(
                {'ParticipantId': 'Customer',
                'ParticipantRole': 'CUSTOMER'})            
            
#        cur_json['Participants'].append(
#            {'ParticipantId': genesys_json['participants'][index]['participantPurpose'].capitalize(),
#            'ParticipantRole': genesys_json['participants'][index]['participantPurpose'].upper()})

    participant_role_to_id = dict()
    for entry in cur_json['Participants']:
        participant_role_to_id[entry['ParticipantRole']] = entry['ParticipantId']

    cur_json['Version'] = '1.1.0'
    cur_json['Transcript'] = list()

    for i in range(len(genesys_json['transcripts'])):
        for phrase in genesys_json['transcripts'][i]['phrases']:
            cur_transcript = dict()
            cur_transcript['Content'] = phrase['text']
            if phrase['participantPurpose'] == 'internal':
                cur_transcript['ParticipantId'] = 'Agent'
            else:
                cur_transcript['ParticipantId'] = 'Customer'
            cur_transcript['Id'] = str(uuid.uuid4())
            cur_json['Transcript'].append(cur_transcript)
    today = datetime.date.today()


    file_name = '{}_analysis_{}_T{}Z.json'.format(cur_str, today.strftime('%Y-%m-%d'), get_random_time())

    return file_name, cur_json

def convert(bucket, key, target):

# Use this code if you want to convert files in Amazon S3
    targetbucket = target

    s3_file = s3.get_object(Bucket=bucket,Key=key)
    genesys_json = s3_file.get('Body').read().decode('utf-8')

    # Transform the file to the Lex Chatbot Designer Format format.
    file_name, chatbot_json = convert_to_chatbot_format(json.loads(genesys_json))

    # Upload the object back into the original bucket under a new path.
    s3.put_object(Bucket=targetbucket,Key=file_name,Body=bytes(json.dumps(chatbot_json).encode('UTF-8')))

    print('[COMPLETE] Successfully transformed [{0}] keys'.format(key))

# if __name__ == '__main__':
#     sys.exit(main())
