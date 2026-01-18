from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from config import Config
from routes.booking_routes import (
    AccommodationBookingResource, TransportBookingResource, 
    AccommodationBookingByID, TransportBookingByID,
    HostBookingsResource, HostAccommodationBookingsResource,
    DriverBookingsResource, DriverTransportBookingsResource
)
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

# Parse CORS_ORIGINS from string to list
cors_origins = app.config.get("CORS_ORIGINS", "")
if isinstance(cors_origins, str):
    cors_origins = [o.strip() for o in cors_origins.split(",") if o.strip()]

CORS(app, supports_credentials=True, origins=cors_origins)
api = Api(app)

app.register_blueprint(auth_bp, url_prefix="/auth")

api.add_resource(TransportBookingResource, '/transport_bookings')
api.add_resource(TransportBookingByID, '/transport_bookings/<int:id>')
api.add_resource(AccommodationBookingResource, '/accommodation_bookings')
api.add_resource(AccommodationBookingByID, '/accommodation_bookings/<int:id>')

# Host booking routes
api.add_resource(HostBookingsResource, '/host/bookings')
api.add_resource(HostAccommodationBookingsResource, '/host/accommodations/<int:accommodation_id>/bookings')

# Driver booking routes
api.add_resource(DriverBookingsResource, '/driver/bookings')
api.add_resource(DriverTransportBookingsResource, '/driver/transports/<int:transport_id>/bookings')

# Register Routes
api.add_resource(AccommodationResource, '/accommodations', '/accommodations/<int:id>')
api.add_resource(TransportResource, '/transports', '/transports/<int:id>')

@app.route("/")
def health_check():
    return {"status": "SafariConnect API running"}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
