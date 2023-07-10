from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_socketio import SocketIO, emit


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/zomato'  # Replace with your MongoDB connection URI
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secret key of your choice
mongo = PyMongo(app)
socketio = SocketIO(app)

# Route for displaying the menu
@app.route('/')
def op():
    return "Welcome"

@app.route('/create_collections')  # This route is for demonstration purposes only
def create_collections():
    # Create 'dishes' collection
    dishes_collection = mongo.db.dishes
    # Create 'orders' collection
    orders_collection = mongo.db.orders

    # Perform any additional setup or initialization here, such as creating indexes

    return 'Collections created successfully!'


# Route for displaying the menu
@app.route('/menu')
def menu():
    dishes = mongo.db.dishes.find()
    return render_template('menu.html', dishes=dishes)

# Route for adding a new dish
@app.route('/add_dish', methods=['GET', 'POST'])
def add_dish():
    if request.method == 'POST':
        dish = {
            'name': request.form['name'],
            'price': request.form['price'],
            'availability': True
        }
        mongo.db.dishes.insert_one(dish)
        return redirect(url_for('menu'))
    return render_template('add_dish.html')

# Route for updating a dish
@app.route('/update_dish/<dish_id>', methods=['GET', 'POST'])
def update_dish(dish_id):
    dish = mongo.db.dishes.find_one({'_id': dish_id})
    if request.method == 'POST':
        updated_dish = {
            'name': request.form['name'],
            'price': request.form['price'],
            'availability': dish['availability']
        }
        mongo.db.dishes.update_one({'_id': dish_id}, {'$set': updated_dish})
        return redirect(url_for('menu'))
    return render_template('update_dish.html', dish=dish)

# Route for deleting a dish
@app.route('/delete_dish/<dish_id>')
def delete_dish(dish_id):
    mongo.db.dishes.delete_one({'_id': dish_id})
    return redirect(url_for('menu'))




# Route for taking a new order
@app.route('/take_order', methods=['GET', 'POST'])
def take_order():
    if request.method == 'POST':
        dish_ids = request.form.getlist('dish_ids[]')
        dishes = mongo.db.dishes.find({'_id': {'$in': [ObjectId(dish_id) for dish_id in dish_ids]}})
        if dishes.count() != len(dish_ids):
            return 'Invalid dish selection. Please try again.'

        order = {
            'customer_name': request.form['customer_name'],
            'dish_ids': dish_ids,
            'status': 'received'
        }
        mongo.db.orders.insert_one(order)
        socketio.emit('new_order', {}, namespace='/')
        return redirect(url_for('menu'))

    dishes = mongo.db.dishes.find()
    return render_template('take_order.html', dishes=dishes)


# Route for updating the status of an order
@app.route('/update_order_status/<order_id>', methods=['GET', 'POST'])
def update_order_status(order_id):
    order = mongo.db.orders.find_one({'_id': ObjectId(order_id)})
    if request.method == 'POST':
        updated_status = request.form['status']
        mongo.db.orders.update_one({'_id': ObjectId(order_id)}, {'$set': {'status': updated_status}})
        socketio.emit('order_status_update', {'order_id': str(order['_id']), 'status': updated_status}, namespace='/')
        return redirect(url_for('menu'))

    return render_template('update_order_status.html', order=order)



@app.route('/chat')
def chat():
    return render_template('chat.html')

@socketio.on('chat_message', namespace='/')
def handle_chat_message(message):
    response = generate_chatbot_response(message)
    emit('chat_response', {'message': response})

def generate_chatbot_response(message):
    # Implement your chatbot logic here
    # Return an appropriate response based on the user's message
    return 'This is a sample response from the chatbot.'







if __name__ == '__main__':
    app.run(debug=True)
