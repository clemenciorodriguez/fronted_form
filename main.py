from flask import Flask, request, jsonify,url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://uftekw6lr9o2a7oq:kfrdejJwCGdj3j8IcrsO@bzc2vs79rtlg1pmcnuf2-mysql.services.clever-cloud.com:3306/bzc2vs79rtlg1pmcnuf2'
db = SQLAlchemy(app)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    detail = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    images = db.relationship('Image', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lastname': self.lastname,
            'detail': self.detail,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'images': [image.to_dict() for image in self.images]
        }

with app.app_context():
    db.create_all()
    print("conected")



@app.route('/users', methods=['POST'])
def add_user():
    name = request.form.get('name')
    lastname = request.form.get('lastname')
    detail = request.form.get('detail')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    user = User(name=name, lastname=lastname, detail=detail, latitude=latitude, longitude=longitude)
    images = request.files.getlist("images")
    
    images_urls = []
    for image in images:
        filename = image.filename 
        image_url = url_for("/", filename="photos/" + filename)
        image.save(os.path.join(app.root_path, "static/photos", filename))
        images_urls.append(Image(url=image_url, user_id=user.id))

    user.images = images_urls

   
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@app.route('/', methods=['GET'])
def get_data():
    data = User.query.all()
    output = []
    for p in data:
        try:
            output.append(p.to_dict())
        except TypeError:
            pass
    return jsonify(output), 200



if __name__ == '__main__':
    app.run(debug=True)