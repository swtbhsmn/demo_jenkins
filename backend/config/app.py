from chalice import (Chalice, Response)
import boto3
import json
app = Chalice(app_name='config')
aws_endpoint_url = "http://localhost:8001"


@app.route('/')
def index():
    return {'hello': 'world'}


@app.route('/filter')
def read_data():
    dynamodb = boto3.client('dynamodb', endpoint_url=aws_endpoint_url)
    table = dynamodb
    partition_key = {
        "AccountId_RuleId": "427615184843_1006"
    }
    sort_key = {
        "Exception": "arn:aws:iam::168473487067:policy/Custom-Role-JenkinsCIAM"
    }
    response = table.scan(
        TableName="RESOURCE",
        FilterExpression="#partition_key = :partition_value and begins_with (#sort_key, :sort_value) and #Status<>:Status",
        ExpressionAttributeNames={
            "#partition_key": [i for i in partition_key.keys()][0],
            "#sort_key": [i for i in sort_key.keys()][0],
            "#Status":"Status"
        },
        ExpressionAttributeValues={
            ":partition_value": {'S': [i for i in partition_key.values()][0]},
            ":sort_value": {'S': [i for i in sort_key.values()][0]},
            ":Status":{'S':"EXCEPTION_DELETE"}
        }
    )
    data = response['Items']
    return Response(body=data)


@app.route('/read')
def read_data():
    dynamodb = boto3.resource('dynamodb', endpoint_url=aws_endpoint_url)
    table = dynamodb.Table('RESOURCE')
    response = table.scan()
    data = response['Items']
    return Response(body=data)

@app.route('/update')
def update_data():
    dynamodb = boto3.resource('dynamodb', endpoint_url=aws_endpoint_url)
    table = dynamodb.Table('RESOURCE')
    key = {
        "AccountId_RuleId": "427615184843_1006",
        "Exception": "arn:aws:iam::168473487067:policy/Custom-Role-JenkinsCIAM"
    }
    table.update_item(
        Key=key,
        UpdateExpression="set ServiceNowTicketId=:s",
        ExpressionAttributeValues={':s': 'EXCEPTION_DELETE'}
    )
    return Response(body={'success': True})

@app.route('/table-lists')
def get_dynamodb_tables():
    try:
        data = []
        dynamodb = boto3.resource('dynamodb', endpoint_url=aws_endpoint_url)
        tables = dynamodb.tables.all()
        if (len(list(tables)) > 0):
            for table in tables:
                data.append(table.name)
            return Response(body={"data": data, "message": "Table found!"})
        else:
            return Response(body={"data": None, "message": "Table not found!"})
    except Exception as err:
        print(err)


@app.route('/create-item')
def create_item():
    dynamodb = boto3.resource('dynamodb', endpoint_url=aws_endpoint_url)
    table = dynamodb.Table('RESOURCE')
    table.put_item(
        TableName='RESOURCE',
        Item={
            "AccountId": "427615184844",
            "AccountId_RuleId": "427615184843_1005",
            "ApprovalDate": "05/16/2022",
            "CreateTimeStamp": "05/16/2022 05:08:29",
            "Exception": "arn:aws:iam::168473487067:policy/Custom-Role-JenkinsCIAM",
            "ExpiryDate": "05/16/2023",
            "LastModifiedBy": "I99383@verisk.com",
            "PeraId": "RITM1234567",
            "RuleId": 1005,
            "RuleName": "DEV-ec2-asg-public-subnet",
            "ServiceNowTicketId": "RITM1234567",
            "Status": "EXCEPTION_DELETE",
            "UpdateTimeStamp": "08/24/2022 16:54:59"
        }
    )
    return Response(body={'success': True})


@app.route('/create-table')
def create_table():
    dynamodb = boto3.resource('dynamodb', endpoint_url=aws_endpoint_url)
    table = dynamodb.create_table(
        TableName='RESOURCE',
        KeySchema=[
            {'AttributeName': 'AccountId_RuleId',
                'KeyType': 'HASH'},  # Partition key
            {'AttributeName': 'Exception', 'KeyType': 'RANGE'}  # Sort key
        ],
        AttributeDefinitions=[
            {'AttributeName': 'AccountId_RuleId', 'AttributeType': 'S'},
            {'AttributeName': 'Exception', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    # Wait until the table exists.
    table.wait_until_exists()
    return Response(body={'success': True})
