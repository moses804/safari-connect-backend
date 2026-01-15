from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from config import Config
from routes.booking_routes import AccommodationBookingResource, TransportBookingResource, AccommodationBookingByID, TransportBookingByID
from extensions import db, bcrypt, jwt
import models 
# Importing routes
from routes.auth_routes import auth_bp
from routes.accommodation_routes import AccommodationResource
from routes.transport import TransportResource


load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)
jwt.init_app(app)

CORS(app, supports_credentials=True, origins=app.config["CORS_ORIGINS"])
api = Api(app)

app.register_blueprint(auth_bp, url_prefix="/auth")

api.add_resource(TransportBookingResource, '/transport_bookings')
api.add_resource(TransportBookingByID, '/transport_bookings/<int:id>')
api.add_resource(AccommodationBookingResource, '/accommodation_bookings')
api.add_resource(AccommodationBookingByID, '/accommodation_bookings/<int:id>')

# Register Routes
api.add_resource(AccommodationResource, '/accommodations', '/accommodations/<int:id>')
api.add_resource(TransportResource, '/transports', '/transports/<int:id>')

@app.route("/")
def health_check():
    return {"status": "SafariConnect API running"}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)