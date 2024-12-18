from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tokens.db'
db = SQLAlchemy(app)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/generate', methods=['POST'])
def generate_jwt():
    data = request.json
    response = requests.get(f'http://microservice1:5000/readAll')
    users = response.json()
    user = next((u for u in users if u['name'] == data['name'] and u['password'] == data['password']), None)
    
    if user:
        token = jwt.encode({
            'id': user['id'],
            'level_of_access': user['level_of_access'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, 'secret', algorithm='HS256')
        
        new_token = Token(token=token)
        db.session.add(new_token)
        db.session.commit()
        return jsonify({'token': token}), 201
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/verify', methods=['POST'])
def verify_jwt():
    token = request.json.get('token')
    try:
        data = jwt.decode(token, 'secret', algorithms=['HS256'])
        return jsonify({'message': 'Token is valid', 'data': data}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

@app.route('/', methods=['GET'])
def hi():
    return jsonify({"message": "JWT service OK!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)