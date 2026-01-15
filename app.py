import os
from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from models import db

# Importing routes
from routes.accommodation_routes import AccommodationListResource, AccommodationDetailResource
from routes.transport_routes import TransportListResource, TransportDetailResource


load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safariconnect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app) # Connect JWT to flask app - Enables create_access_token and @jwt_required() decorator
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])



# Register Routes
api.add_resource(AccommodationListResource)


if __name__ == '__main__':
    app.run(debug=True, port=5000)