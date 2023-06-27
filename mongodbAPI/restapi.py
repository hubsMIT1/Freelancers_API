from flask import Flask,request,jsonify
from flask import Flask, jsonify, request
from pymongo import MongoClient
from dotenv import load_dotenv
from flask_cors import CORS,cross_origin
import os
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Connect to MongoDB Atlas
client = MongoClient(os.environ.get('MONGO_DB'))
db = client["freelancers"]
collection = db["details_data"]

app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST"], "headers": "Content-Type"}})

@app.route('/')
def home():
    return "<h1> Open the /freelancers</h1>"

@app.route('/freelancers')
def get_data():
    #pagination
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('limit', 10))
    total_documents = collection.count_documents({})
    total_pages = (total_documents - 1) // page_size + 1

    if page > total_pages:
        return jsonify({'message': 'Invalid page number'})

    skip = (page - 1) * page_size
    #skip the data and fetch from where calling
    freelancer_data = list(collection.find({}).skip(skip).limit(page_size))
    
    #do change the mongo json id into string
    formatted_data = [{**data, '_id': str(data['_id'])} for data in freelancer_data]

    return jsonify({
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'total_documents': total_documents,
        'data': formatted_data
    }) 

#inserting new data
@app.route('/freelancers', methods=['POST'])
def insert_data():
    prompt_data = request.json
    collection.insert_one(prompt_data)
    return jsonify({'message':'New Freelancer added'})


#to search the data
@app.route('/freelancers/search/<string:var>', methods=['GET'])
def search_freelancers(var):
    #if the var is number
    try:
        var_lower = int(var)
        query = {
            '$or': [
                {'phone_number': {'$eq': var_lower} },
                {'followers': {'$eq': var_lower }}
            ]
        }
    #if the var is string, there was some issue so i seperated both
    except ValueError:
        var_lower = var.lower()

        query = {
            '$or': [
                {'first_name': {'$regex': var_lower , '$options': 'i'}},
                {'last_name': {'$regex': var_lower , '$options': 'i'}},
                {'email': {'$regex': var_lower , '$options': 'i'}},
                
            ]
        }
    
    search_results = list(collection.find(query))
    formatted_data = [{**data, '_id': str(data['_id'])} for data in search_results]   
    if search_results:
        return jsonify({'results': formatted_data})
    else:
        return jsonify({'message': 'No matching results found.'})
