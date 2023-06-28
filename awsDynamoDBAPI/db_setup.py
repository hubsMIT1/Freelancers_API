import boto3
from botocore.exceptions import ClientError

def create_dynamodb_table():
    dynamodb = boto3.resource('dynamodb')
    table_name = 'freelancerList'

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
                # {
                #     'AttributeName': 'count',
                #     'KeyType': 'RANGE'
                # },

            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                },
                # {
                #     'AttributeName': 'count',
                #     'AttributeType': 'N'
                # },

            ],
            
            BillingMode='PAY_PER_REQUEST'
        )

        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table '{table_name}' created successfully.")
    except ClientError as e:
        print(f"Error creating table '{table_name}': {e.response['Error']['Message']}")

if __name__ == '__main__':
    create_dynamodb_table()