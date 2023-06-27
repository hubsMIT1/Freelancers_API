from flask import Flask, jsonify, request
from flask_cors import CORS
import boto3
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST"], "headers": "Content-Type"}})
# connect with aws dynamodb table 
print(os.environ.get('AWS_ACCESS_KEY_ID'))

dynamodb = boto3.resource('dynamodb', aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
   aws_secret_access_key = os.environ.get('AWS_SRT_ACCESS_KEY'),
   region_name = os.environ.get('REGION_NAME'))
table_name = 'freelancerList' 
table = dynamodb.Table(table_name)

#there i too many difficulty i was facing bcz didn't use the elasticSearch(anyother),lambda and api gateway with dynamodb skip pagination and search case senstive 
# so i just use my way -- (not a good way )

res = table.scan()
itemss = res['Items']
@app.route('/')
def home():
    return "<h1> Open the /freelancers</h1>"

@app.route('/freelancers', methods=['GET'])
def get_items():
    
    # pagination 
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('limit', 10))
    skip = (page-1)*page_size
    
    #if not form staring there where problem when im trying to use last_evaluated_key.. if i'm choosing 5th page from 2nd page so there last key of 2nd that ll open the data of 2nd that was making infinite pages
    
    #so by using the partition id from (1 to N) 
    if(skip>0):
        response = table.scan(
            ExclusiveStartKey={'id':skip},
            Limit=page_size,
        )
    else:
        response = table.scan(
            Limit=page_size,
        )
        
    items = response['Items']
    # items.sort(key=lambda x: x['id'], reverse=False)
    total_documents = res['Count']
    total_pages = (total_documents - 1) // page_size + 1
    print(total_documents, page_size,skip )

    if page > total_pages:
        return jsonify({'message': 'Invalid page number or no data found'})
    # last_evaluated_key = response.get('LastEvaluatedKey', {}).get('id')
    return jsonify({
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'total_documents': total_documents,
        # 'last_evaluated_key': last_evaluated_key,
        'data': items
    })
# didn't create the sort key 
ind = res["Count"]

#insert the data 
@app.route('/freelancers', methods=['POST'])
def insert_data():
    prompt_data = request.json
    #this column i made to search the data by lower case 
    srch =  prompt_data['first_name'].lower() + " " + prompt_data['last_name'].lower()+ " " + prompt_data['email'].lower()
    prompt_data["searchIndex"] = srch
    id = ind+1
    prompt_data["id"] = id #partition id
    
    response = table.put_item(Item=prompt_data)
    
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        ind+=1
        return jsonify({'message': 'New Freelancer added'})
    else:
        return jsonify({'message': 'Failed to add new Freelancer'})
        
#serch the item 
@app.route('/freelancers/search/<string:var>', methods=['GET'])
def search_freelancers(var):
    try:
        var_lower = int(var)
    except ValueError:
        var_lower = var.lower()
    query = {
        "FilterExpression": (   
            "contains(first_name, :var) OR "
            "contains(last_name, :var) OR "
            "contains(email, :var) OR "
            "contains(searchIndex, :var_lower) OR "
            "phone_number= :var_lower OR "
            "followers= :var_lower"
        ),
        "ExpressionAttributeValues": {
           ":var_lower": var_lower,
           ":var":var
        }
    }
    response = table.scan(**query)
    search_results = response.get('Items', [])
    search_results.sort(key=lambda x: x['id'], reverse=False)
    
    if search_results:
        return jsonify({'results': search_results})
    else:
        return jsonify({'message': 'No matching results found.'})
    
if __name__ == '__main__':
    app.run(debug=True)