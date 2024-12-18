from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.db'
db = SQLAlchemy(app)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(200), nullable=False)

# Create the database tables within an application context
with app.app_context():
    db.create_all()

def token_required(f):
    @wraps(f)  # Preserve the original function's metadata
    def decorator(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token is missing!'}), 403
        
        token = auth_header.split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        
        # Call Microservice2 to verify the token
        response = requests.post('http://microservice2:5000/verify', json={'token': token})
        if response.status_code != 200:
            return jsonify({'message': response.json()['message']}), 403
        
        # If token is valid, pass the data to the wrapped function
        return f(response.json()['data'], *args, **kwargs)
    return decorator

@app.route('/create', methods=['POST'])
@token_required
def create_test(data):
    if data['level_of_access'] > 2:
        new_test = Test(data=request.json['data'])
        db.session.add(new_test)
        db.session.commit()
        return jsonify({"message": "Test created"}), 201
    return jsonify({"message": "Access denied"}), 403

@app.route('/readAll', methods=['GET'])
@token_required
def read_all_tests(data):
    tests = Test.query.all()
    return jsonify([{"id": test.id, "data": test.data} for test in tests])

@app.route('/readOne/<int:id>', methods=['GET'])
@token_required
def read_one_test(data, id):
    test = Test.query.get_or_404(id)
    return jsonify({"id": test.id, "data": test.data})

@app.route('/update/<int:id>', methods=['PUT'])
@token_required
def update_test(data, id):
    if data['level_of_access'] > 2:
        test = Test.query.get_or_404(id)
        test.data = request.json['data']
        db.session.commit()
        return jsonify({"message": "Test updated"})
    return jsonify({"message": "Access denied"}), 403

@app.route('/delete/<int:id>', methods=['DELETE'])
@token_required
def delete_test(data, id):
    if data['level_of_access'] > 2:
        test = Test.query.get_or_404(id)
        db.session.delete(test)
        db.session.commit()
        return jsonify({"message": "Test deleted"})
    return jsonify({"message": "Access denied"}), 403

@app.route('/', methods=['GET'])
def hi():
    return jsonify({"message": "Test service OK!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)