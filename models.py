from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from extensions import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum("tourist", "host","driver", name="user_roles"), default="tourist", nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    accommodations = db.relationship('Accommodation', back_populates='host', cascade='all, delete-orphan')
    transports = db.relationship('Transport', back_populates='driver', cascade='all, delete-orphan')
    accommodation_bookings = db.relationship('AccommodationBooking', back_populates='tourist', cascade='all, delete-orphan')
    transport_bookings = db.relationship('TransportBooking', back_populates='tourist', cascade='all, delete-orphan')

        # -------- AUTH HELPERS --------
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    #when the get method by id is called it will show both accommodation and transport bookings without password hash
    serializer_rules = (
        '-password_hash',
        '-accommodations',                    # Prevent User→accommodations circular reference
        '-accommodations.host',               # Prevent deeper nesting
        '-accommodations.bookings',
        '-transports',                        # Prevent User→transports circular reference
        '-transports.driver',
        '-transports.bookings',
        '-accommodation_bookings',            # Prevent User→booking circular reference
        '-accommodation_bookings.tourist',
        '-accommodation_bookings.accommodation',
        '-transport_bookings',                # Prevent User→booking circular reference
        '-transport_bookings.tourist',
        '-transport_bookings.transport',
        )

class Accommodation(db.Model, SerializerMixin):
    __tablename__ = 'accommodations'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    location = db.Column(db.String(), nullable=False)
    available= db.Column(db.Boolean, default=True, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    host = db.relationship('User', back_populates='accommodations')
    bookings = db.relationship('AccommodationBooking', back_populates='accommodation', cascade='all, delete-orphan')

    def to_dict(self, include_relationships=False):
        """Custom to_dict to prevent infinite recursion."""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'available': self.available,
            'price_per_night': self.price_per_night,
            'capacity': self.capacity,
            'host_id': self.host_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_relationships:
            # Include host info but NOT nested relationships from host
            data['host'] = {
                'id': self.host.id,
                'name': self.host.name,
                'email': self.host.email,
                'phone_number': self.host.phone_number,
            }
            # Include bookings summary but avoid recursion
            data['bookings'] = [{
                'id': b.id,
                'check_in_date': b.check_in_date.isoformat() if b.check_in_date else None,
                'check_out_date': b.check_out_date.isoformat() if b.check_out_date else None,
                'total_price': b.total_price,
                'status': b.status,
            } for b in self.bookings]
        
        return data



class Transport(db.Model,SerializerMixin):
    __tablename__ = 'transports'
    
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_type = db.Column(db.String(), nullable=False)
    available = db.Column(db.Boolean, default=True, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    total_capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

   
    driver = db.relationship('User', back_populates='transports')
    bookings = db.relationship('TransportBooking', back_populates='transport', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self, include_relationships=False):
        """Custom to_dict to prevent infinite recursion."""
        data = {
            'id': self.id,
            'driver_id': self.driver_id,
            'vehicle_type': self.vehicle_type,
            'available': self.available,
            'price_per_day': self.price_per_day,
            'total_capacity': self.total_capacity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_relationships:
            # Include driver info but NOT nested relationships from driver
            data['driver'] = {
                'id': self.driver.id,
                'name': self.driver.name,
                'email': self.driver.email,
                'phone_number': self.driver.phone_number,
            }
            # Include bookings summary but avoid recursion
            data['bookings'] = [{
                'id': b.id,
                'travel_date': b.travel_date.isoformat() if b.travel_date else None,
                'seats_booked': b.seats_booked,
                'total_price': b.total_price,
                'status': b.status,
            } for b in self.bookings]
        
        return data

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

    serializer_rules = (
        '-tourist',                              # Prevent booking→tourist circular reference
        '-tourist.password_hash',
        '-tourist.accommodations',
        '-tourist.transports',
        '-tourist.accommodation_bookings',
        '-tourist.transport_bookings',
        '-accommodation',                        # Prevent booking→accommodation circular reference
        '-accommodation.host',
        '-accommodation.bookings',
        '-accommodation.host.password_hash',
        '-accommodation.host.accommodations',
        '-accommodation.host.transports',
        '-accommodation.host.accommodation_bookings',
        '-accommodation.host.transport_bookings',
    )


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

    serializer_rules = (
        '-tourist',                              # Prevent booking→tourist circular reference
        '-tourist.password_hash',
        '-tourist.accommodations',
        '-tourist.transports',
        '-tourist.accommodation_bookings',
        '-tourist.transport_bookings',
        '-transport',                            # Prevent booking→transport circular reference
        '-transport.driver',
        '-transport.bookings',
        '-transport.driver.password_hash',
        '-transport.driver.accommodations',
        '-transport.driver.transports',
        '-transport.driver.accommodation_bookings',
        '-transport.driver.transport_bookings',
    )
    
