from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
import time
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow all origins


def connect_to_mongo():
    retries = 5
    for i in range(retries):
        try:
            # Updated for Docker
            client = MongoClient('mongodb://mongodb:27017/')
            return client['todoapp']['todos']
        except Exception as e:
            print(f"Connection attempt {i + 1} failed: {e}")
            time.sleep(2)
    raise Exception("Could not connect to MongoDB after multiple attempts")


todos_collection = connect_to_mongo()


@app.route('/api/message', methods=['GET'])
def get_message():
    return jsonify({"message": "working"}), 200

# Check MongoDB connection


@app.route('/api/check_connection', methods=['GET'])
def check_connection():
    try:
        # Try to retrieve one document from the todos collection
        todos = todos_collection.find_one()
        if todos:
            return jsonify({"message": "Connection successful", "todos": todos}), 200
        else:
            return jsonify({"message": "Connection successful, but no todos found"}), 200
    except Exception as e:
        return jsonify({"message": "Connection failed", "error": str(e)}), 500

# Create a new todo


@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.json
    todo_id = todos_collection.insert_one({
        "title": data['title'],
        "completed": data.get('completed', False)
    }).inserted_id
    todo = todos_collection.find_one({"_id": todo_id})
    return jsonify({"id": str(todo['_id']), "title": todo['title'], "completed": todo['completed']}), 201

# Read all todos


@app.route('/api/todos', methods=['GET'])
def get_todos():
    todos = []
    for todo in todos_collection.find():
        todos.append(
            {"id": str(todo['_id']), "title": todo['title'], "completed": todo['completed']})
    return jsonify(todos), 200

# Update a todo


@app.route('/api/todos/<id>', methods=['PUT'])
def update_todo(id):
    data = request.json
    todos_collection.update_one({"_id": ObjectId(id)}, {"$set": {
        "title": data['title'],
        "completed": data['completed']
    }})
    todo = todos_collection.find_one({"_id": ObjectId(id)})
    return jsonify({"id": str(todo['_id']), "title": todo['title'], "completed": todo['completed']}), 200

# Delete a todo


@app.route('/api/todos/<id>', methods=['DELETE'])
def delete_todo(id):
    todos_collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Todo deleted"}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
