from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    level_of_access = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/create', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(name=data['name'], password=data['password'], level_of_access=data['level_of_access'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User  created"}), 201

@app.route('/readAll', methods=['GET'])
def read_all_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name, "password": user.password, "level_of_access": user.level_of_access} for user in users])

@app.route('/readOne/<int:id>', methods=['GET'])
def read_one_user(id):
    user = User.query.get_or_404(id)
    return jsonify({"id": user.id, "name": user.name, "password": user.password, "level_of_access": user.level_of_access})

@app.route('/update/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.json
    user.name = data['name']
    user.password = data['password']
    user.level_of_access = data['level_of_access']
    db.session.commit()
    return jsonify({"message": "User  updated"})

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User  deleted"})

@app.route('/', methods=['GET'])
def hi():
    return jsonify({"message": "User service OK!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)