import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ContactFormMessages')
ses = boto3.client('ses')

SENDER_EMAIL = "shaikrohanbaba2023@gmail.com"  # must match your SES verified identity
RECIPIENT_EMAIL = "shaikrohanbaba2023@gmail.com"  # same email is fine for a personal project

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        name = body.get('name', 'Anonymous')
        email = body.get('email', 'not provided')
        message = body.get('message', '')

        if not message:
            return response(400, {"error": "Message cannot be empty"})

        # Store in DynamoDB
        message_id = str(uuid.uuid4())
        table.put_item(Item={
            'messageId': message_id,
            'name': name,
            'email': email,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })

        # Send email via SES
        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [RECIPIENT_EMAIL]},
            Message={
                'Subject': {'Data': f'New contact form message from {name}'},
                'Body': {'Text': {'Data': f"From: {name} ({email})\n\n{message}"}}
            }
        )

        return response(200, {"success": True, "messageId": message_id})

    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {"error": "Something went wrong"})

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps(body)
    }
