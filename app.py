from flask import Flask, request, jsonify
import boto3
import uuid
from datetime import datetime

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb')
inventory_table = dynamodb.Table('Inventory')
orders_table = dynamodb.Table('Orders')

@app.route('/items', methods=['GET'])
def get_items():
    response = inventory_table.scan()
    return jsonify(response['Items'])

@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    item_id = str(uuid.uuid4())
    inventory_table.put_item(
        Item={
            'ItemId': item_id,
            'Name': data['name'],
            'Quantity': int(data['quantity'])
        }
    )
    return jsonify({'message': 'Item added successfully!'})

@app.route('/items', methods=['PUT'])
def update_item():
    data = request.get_json()
    inventory_table.update_item(
        Key={'ItemId': data['ItemId']},
        UpdateExpression='SET Name = :name, Quantity = :quantity',
        ExpressionAttributeValues={
            ':name': data['Name'],
            ':quantity': int(data['Quantity'])
        }
    )
    return jsonify({'message': 'Item updated successfully!'})

@app.route('/items', methods=['DELETE'])
def delete_item():
    data = request.get_json()
    inventory_table.delete_item(
        Key={'ItemId': data['ItemId']}
    )
    return jsonify({'message': 'Item deleted successfully!'})

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    order_id = str(uuid.uuid4())
    order_date = datetime.now().isoformat()
    items = data['items']

    for item in items:
        inventory_table.update_item(
            Key={'ItemId': item['ItemId']},
            UpdateExpression='SET Quantity = Quantity - :quantity',
            ExpressionAttributeValues={':quantity': int(item['Quantity'])}
        )

    orders_table.put_item(
        Item={
            'OrderId': order_id,
            'OrderDate': order_date,
            'Items': items
        }
    )
    return jsonify({'message': 'Order created successfully!', 'OrderId': order_id})

@app.route('/orders', methods=['GET'])
def list_orders():
    response = orders_table.scan()
    return jsonify(response['Items'])

@app.route('/upcoming-orders', methods=['GET'])
def list_upcoming_orders():
    # Mocked data for example
    upcoming_orders = [
        {'OrderId': '1', 'ExpectedDate': '2024-07-30', 'Items': [{'Name': 'Item 1', 'Quantity': 10}]},
        {'OrderId': '2', 'ExpectedDate': '2024-08-01', 'Items': [{'Name': 'Item 2', 'Quantity': 5}]}
    ]
    return jsonify(upcoming_orders)

if __name__ == '__main__':
    app.run(debug=True)
