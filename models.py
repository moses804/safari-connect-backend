from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy import MetaData
from datetime import datetime

# Naming convention for constraints
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)

db = SQLAlchemy(metadata=metadata)


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum("tourist", "host","driver", name="user_roles"), default="tourist", nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    accommodations = db.relationship('Accommodation', back_populates='host', cascade='all, delete-orphan')
    transports = db.relationship('Transport', back_populates='driver', cascade='all, delete-orphan')
    accommodation_bookings = db.relationship('AccommodationBooking', back_populates='tourist', cascade='all, delete-orphan')
    transport_bookings = db.relationship('TransportBooking', back_populates='tourist', cascade='all, delete-orphan')



class Accommodation(db.Model, SerializerMixin):
    __tablename__ = 'accommodations'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    location = db.Column(db.String(), nullable=False)
    available= db.Column(db.Boolean, default=True, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


    host = db.relationship('User', back_populates='accommodations')
    bookings = db.relationship('AccommodationBooking', back_populates='accommodation', cascade='all, delete-orphan')



class Transport(db.Model,SerializerMixin):
    __tablename__ = 'transports'
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_type = db.Column(db.String(), nullable=False)
    available = db.Column(db.Boolean, default=True, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

   
    driver = db.relationship('User', back_populates='transports')
    bookings = db.relationship('TransportBooking', back_populates='transport', cascade='all, delete-orphan', lazy='dynamic')

class AccommodationBooking(db.Model, SerializerMixin):
    __tablename__ = 'accommodation_bookings'
    id = db.Column(db.Integer, primary_key=True)
    tourist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    accommodation_id = db.Column(db.Integer, db.ForeignKey('accommodations.id'), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum("pending", "confirmed", "cancelled", name="booking_status"), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    
    tourist = db.relationship('User', back_populates='accommodation_bookings')
    accommodation = db.relationship('Accommodation', back_populates='bookings')


class TransportBooking(db.Model, SerializerMixin):
    __tablename__ = 'transport_bookings'
    id = db.Column(db.Integer, primary_key=True)
    tourist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transport_id = db.Column(db.Integer, db.ForeignKey('transports.id'), nullable=False)
    travel_date = db.Column(db.Date, nullable=False)
    seats_booked = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum("pending", "confirmed", "cancelled", name="booking_status"), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


    tourist = db.relationship('User', back_populates='transport_bookings')
    transport = db.relationship('Transport', back_populates='bookings')

# WIP - Models here