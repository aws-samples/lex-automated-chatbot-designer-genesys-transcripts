
# genesys-lex-automated-chatbot-designer


![Architecture Diagram](/Genesys-EventBridge-Lexdesigner.jpg)


## About the project

This project contains source code and supporting files for a serverless application that you can deploy with AWS SAM CLI. It includes the following files and folders.

  

- ConvertToLexFormat - Code for Lambda function which will ingest a file from the RawTranscript s3 bucket, convert the transcript to format readable by lex designer and then write the output to the TransformedTranscript bucket.
- ReadFromEBandWritetoS3  - Code for Lambda function which will ingest the transcribe events from Genesys Cloud Cx through the event bridge, filter out unwanted events and write the appropriate transcribe event to the RawTranscript S3 bucket.

- events - Invocation events that you can use to invoke the function.

- tests - Unit tests for the application code.

- template.yaml - A template that defines the application's AWS resources. 

  

The application uses several AWS resources, including AWS Lambda functions , Amazon Event Bridge , Amazon Event Bridge rules and Amazon S3 buckets. These resources are defined in the `template.yaml` file in this project.
 
## Prerequisites

Before deploying the application the following needs to be set up

 - A valid Genesys Cloud CX environment with an organization. 
 - A valid AWS account.
 - Amazon EventBridge integration on the Genesys Cloud CX application. Once this is set up capture the bus name from the EventBridge instance.
 - Configure OAuth credentials (Client_id , Client_secret) on the Genesys Cloud CX application instance.
 

  

## Deploy the  application

  

Please Install SAM CLI before proceeding to the next steps. The instructions are available at https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

To build and deploy the application for the first time, run the following in your shell:

 

```bash

sam  build  --use-container

sam  deploy  --guided

```

  

The first command will build the source of your application. The second command will package and deploy your application to AWS, with a series of prompts:

  

 * **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.

 * **AWS Region**: The AWS region you want to deploy your app to. Make sure it is deployed in the same region as the Event bridge
 * **Parameter GenesysBusname**: This is the bus name created when Genesys integratoin is configured.  As mentioned in the prerequisites section enter the name of the bus here. The pattern of the bus name should look like `aws.partner/genesys.com/*`
 * **Parameter ClientId**: This is mentioned in the prerequisite section , copy the parameter  value from Genesys Cloud CX.
 * **Parameter ClientSecret**: This is mentioned in the prerequisite section , copy the parameter  value from Genesys Cloud CX.
 * **Parameter FileNamePrefix**: This is the file name prefix for the target transcript file in the raw bucket. There is a default value associated with it, but can be changed.

 * **Parameter GenCloudEnv**: This is the cloud environment for the specific Genesys organization. Genesys is available in more than 15 regions world wide today, so this value is mandatory and should point to the environment where your organizatoin is created in Genesys eg: usw2.pure.cloud
 * 
 * **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes. 

 * **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.

 * **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.



  ## Post Deployment Steps

 * Make a call to Genesys to create a transcript
 * Wait for a couple of minutes and check the TransformedTranscript bucket for the output
 * Once you have sufficient amount of transcripts, utilize Amazon Lex Automated Chatbot Designer to build your first bot. For the required number of transcripts, please refer to the Amazon Lex documentation [here](https://docs.aws.amazon.com/lexv2/latest/dg/designing-import.html). 
 

  



  

