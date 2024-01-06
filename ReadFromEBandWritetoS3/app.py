import json
import boto3
from datetime import datetime
import json
import os
import base64, requests, sys
#import PureCloudPlatformClientV2
# import requests
def genToken(clientid, clientsecret,genesysenv,httptimeout):
       # Base64 encode the client ID and client secret
    

    authorization = base64.b64encode(bytes(clientid + ":" + clientsecret, "ISO-8859-1")).decode("ascii")

    # Prepare for POST /oauth/token request
    request_headers = {
        "Authorization": f"Basic {authorization}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    request_body = {
        "grant_type": "client_credentials"
    }
    

    # Get token
    response = requests.post(f"https://login.{genesysenv}/oauth/token", data=request_body, headers=request_headers,timeout=httptimeout)

    # Check response
    if response.status_code == 200:
        print("Got token")
    else:
        print(f"Failure: { str(response.status_code) } - { response.reason }")
        sys.exit(response.status_code)

    # Get JSON response body
    response_json = response.json()
  

    # Prepare for GET /api/v2/authorization/roles request
    requestHeaders = {
        "Authorization": f"{ response_json['token_type'] } { response_json['access_token']}"
    }

    return requestHeaders

def filterEvents(event) :
    topic = event['detail']['topicName']
    #status = 
    if topic.__contains__('v2.conversations.') and event['detail']['eventBody']['status']['status'] == 'SESSION_ENDED':
        response = {
            "conversationId": f"{event['detail']['eventBody']['conversationId']}",
            "communicationId": f"{event['detail']['eventBody']['communicationId']}"
        }
       # print(f"event topic is  {topic}")
        return response
    else:
       # print(f"event topic is  {topic}")
        response = {
            "conversationId": "NA",
            "communicationId": "NA"
        }
        return response

def getJsonPayload(conversationdetails,requestheaders,genesysenv,httptimeout):

        response = requests.get(f"https://api.{genesysenv}/api/v2/speechandtextanalytics/conversations/{conversationdetails['conversationId']}/communications/{conversationdetails['communicationId']}/transcripturl", 
                              headers=requestheaders,
                              timeout=httptimeout)
           # Check response
        if response.status_code == 200:
            print("Got response")
        else:
            print(f"Failure: { str(response.status_code) } - { response.reason }")
            sys.exit(response.status_code)

        jsonpayLoad = response.json()
        actualpayload=requests.get(jsonpayLoad['url'],timeout=httptimeout)

        return actualpayload.json()

def writetos3(payload, bucket , fileprefix):
    s3 = boto3.resource('s3')
   # s3://anbose-test-learning/event-bridge/sqs-events/
   # Getting the current date and time
    dt = datetime.now()
    #print("Event is::",event)
# getting the timestamp
    ts = datetime.timestamp(dt)
    file_name = fileprefix+str(ts)+'.json'
  #  print("Json Data is::",body)
    print(f"writing data to the bucket::{bucket}::folder::{fileprefix}")
    s3object = s3.Object(bucket,file_name )
    print(f"created connection to the bucket::{bucket}::folder::{fileprefix}")

    s3object.put(
        Body=(bytes(json.dumps(payload).encode('UTF-8')))
    )
    print(f"wrote data to the bucket::{bucket}::folder::{fileprefix}")

def lambda_handler(event, context):



    # URL to hit is https://api.usw2.pure.cloud/api/v2/speechandtextanalytics/conversations/f7901c1e-c682-4b1c-89ae-e714257b0cf9/communications/765d9019-12bd-4108-976f-c12c9d428a59/transcripturl
    #


    clientid = os.environ['clientid']
    clientsecret = os.environ['clientsecret']
    bucketname = os.environ['bucketname']
    fileprefix = os.environ['fileprefix']
    genesysenv = os.environ['genesysenv'] # eg. mypurecloud.com
    httptimeout = os.environ['httptimeout'] # This was added because of the warnings
    
    # Fliter out events
    resp=filterEvents(event)
    if (resp['conversationId'] == 'NA'):
       # print ("The Event Filtered out  is::",json.dumps(event))
        sys.exit(200)
    
    print ("The Event is not filtered and it is::",json.dumps(resp))

    # Now generate the token
    reqHeader = genToken(clientid, clientsecret,genesysenv,httptimeout)
    # Now invoke the function to get the transcript
    payload = getJsonPayload(resp,reqHeader,genesysenv,httptimeout)

    print ("The Json Conversation payload  is::",json.dumps(payload))
    # Now write to S3
    writetos3(payload,bucketname,fileprefix)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }


