# SDK 

import boto3
import os

def lambda_handler(event, context):

    """
    Using sdk, we are putting our threshold email specific fields in our dynamodb table, table we already created in stack
    because it's part of infrastructure, here we putting values in table
    :Args:
    event: using this parameter, we will get our desired attribute to push into table 
    :return: dictionary of string

    """

    #Read SNS Notification from event parameter
    # Get table name from environment variable
    tableName = os.environ['NameOfTable']
    #Parse the fields in the field & Pick and choose the information that you want to place in you db table
    message_id = event['Records'][0]['Sns']['MessageId']
    timeStamp = event['Records'][0]['Sns']['TimeStamp']
        
    #4. write to the table  
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.put_item
    
    client = boto3.client('dynamodb')
    return client.put_item(
        TableName = tableName,
        Item = {
            'id':{
                'S': message_id,
            },
            'timeStamp':{
                'S': timeStamp,
            }
        }
    )
