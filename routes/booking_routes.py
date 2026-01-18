from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from schemas.booking_schema import parser, transport_parser
from models import db, AccommodationBooking, TransportBooking, Accommodation, Transport
from routes.transport import TransportResource


class TransportBookingResource(Resource):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        data = transport_parser.parse_args()
        
        transport = Transport.query.filter_by(id=data['transport_id']).with_for_update().first()
        if not transport:
            return {"message": "Transport not found"}, 404
        
        # Calculate already booked seats for that date
        booked_seats = db.session.query(db.func.sum(TransportBooking.seats_booked)).filter(
            TransportBooking.transport_id == data['transport_id'],
            TransportBooking.travel_date == data['travel_date']
        ).scalar() or 0
        
        # Check if new booking exceeds capacity
        if booked_seats + data['seats_booked'] > transport.total_capacity:
            return {"message": "Not enough seats available on this date"}, 400


        # new transport instance
        trans_inputs = TransportBooking(**data)
        trans_inputs.tourist_id = current_user_id
        # save to database
        db.session.add(trans_inputs)
        db.session.commit()
        return {
            "message": "Transport booking created successfully", 
            "booking_id": trans_inputs.id
        }, 201
    
    @jwt_required()
    def get(self):
        # Get user identity and role from JWT
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        if role == 'tourist':
            # Tourists see only their own bookings
            bookings = TransportBooking.query.filter_by(tourist_id=current_user_id).all()
        elif role == 'driver':
            # Drivers see bookings for their transport
            bookings = TransportBooking.query.join(Transport).filter(
                Transport.driver_id == current_user_id
            ).all()
        elif role == 'host':
            # Hosts see all transport bookings (or can be restricted)
            bookings = TransportBooking.query.all()
        else:
            return {"message": "Invalid role"}, 403

        return [{
            'id': b.id,
            'tourist_id': b.tourist_id,
            'transport_id': b.transport_id,
            'travel_date': b.travel_date.isoformat() if b.travel_date else None,
            'seats_booked': b.seats_booked,
            'total_price': b.total_price,
            'status': b.status,
            'created_at': b.created_at.isoformat() if b.created_at else None
        } for b in bookings], 200
        
class TransportBookingByID(Resource):
    @jwt_required()
    def get(self, id):
        # Get user identity and role from JWT
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        booking = TransportBooking.query.filter_by(id=id).first()
        if not booking:
            return {"message": "Transport booking not found"}, 404
        
        # Role-based access control for viewing
        if role == 'tourist' and booking.tourist_id != current_user_id:
            return {"message": "Access denied"}, 403
        elif role == 'driver':
            # Check if the booking is for their transport
            transport = Transport.query.get(booking.transport_id)
            if not transport or transport.driver_id != current_user_id:
                return {"message": "Access denied"}, 403

        return {
            'id': booking.id,
            'tourist_id': booking.tourist_id,
            'transport_id': booking.transport_id,
            'travel_date': booking.travel_date.isoformat() if booking.travel_date else None,
            'seats_booked': booking.seats_booked,
            'total_price': booking.total_price,
            'status': booking.status,
            'created_at': booking.created_at.isoformat() if booking.created_at else None
        }, 200
    
    @jwt_required()
    def patch(self, id):
        # Get user identity and role from JWT
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        booking = TransportBooking.query.filter_by(id=id).first()
        if not booking:
            return {"message": "Transport booking not found"}, 404
        
        # Role-based access control for updating
        if role == 'tourist' and booking.tourist_id != current_user_id:
            return {"message": "Access denied"}, 403
        elif role == 'driver':
            # Check if the booking is for their transport
            transport = Transport.query.get(booking.transport_id)
            if not transport or transport.driver_id != current_user_id:
                return {"message": "Access denied"}, 403
        
        # Parse arguments
        data = transport_parser.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(booking, key, value)

        db.session.commit()
        return {
            'id': booking.id,
            'tourist_id': booking.tourist_id,
            'transport_id': booking.transport_id,
            'travel_date': booking.travel_date.isoformat() if booking.travel_date else None,
            'seats_booked': booking.seats_booked,
            'total_price': booking.total_price,
            'status': booking.status,
            'created_at': booking.created_at.isoformat() if booking.created_at else None
        }, 200
    
    @jwt_required()
    def delete(self, id):
        # Get user identity and role from JWT
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        booking = TransportBooking.query.filter_by(id=id).first()
        if not booking:
            return {"message": "Transport booking not found"}, 404
        
        # Role-based access control for deleting
        if role == 'tourist' and booking.tourist_id != current_user_id:
            return {"message": "Access denied"}, 403
        elif role == 'driver':
            # Check if the booking is for their transport
            transport = Transport.query.get(booking.transport_id)
            if not transport or transport.driver_id != current_user_id:
                return {"message": "Access denied"}, 403
        
        db.session.delete(booking)
        db.session.commit()
        return {"message": "Transport booking deleted successfully"}, 200
    

class AccommodationBookingResource(Resource):
    @jwt_required()
    def post(self):
        # Get user identity and role from JWT
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        # Parse data using your accommodation-specific parser
        data = parser.parse_args()
        
        # Set tourist_id to current user (from JWT)
        data['tourist_id'] = current_user_id
        
        # Extra validation
        if data['check_out_date'] <= data['check_in_date']:
            return {"message": "check_out_date must be after check_in_date"}, 400

        # Check for overlapping bookings
        conflict = AccommodationBooking.query.filter(
            AccommodationBooking.accommodation_id == data['accommodation_id'],
            AccommodationBooking.check_in_date < data['check_out_date'],
            AccommodationBooking.check_out_date > data['check_in_date']
        ).first()

        if conflict:
            return {"message": "Dates already booked for this accommodation"}, 409

        
        # Create new instance
        new_booking = AccommodationBooking(**data)
        
        db.session.add(new_booking)
        db.session.commit()
        
        return {
            "message": "Accommodation booking created successfully", 
            "booking_id": new_booking.id
        }, 201

    @jwt_required()
    def get(self):
        # Get user identity and role from JWT
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        if role == 'tourist':
            # Tourists see only their own bookings
            bookings = AccommodationBooking.query.filter_by(tourist_id=current_user_id).all()
        elif role == 'host':
            # Hosts see bookings for their accommodations
            bookings = AccommodationBooking.query.join(Accommodation).filter(
                Accommodation.host_id == current_user_id
            ).all()
        elif role == 'driver':
            # Drivers can see all accommodation bookings
            bookings = AccommodationBooking.query.all()
        else:
            return {"message": "Invalid role"}, 403

        return [{
            'id': b.id,
            'tourist_id': b.tourist_id,
            'accommodation_id': b.accommodation_id,
            'check_in_date': b.check_in_date.isoformat() if b.check_in_date else None,
            'check_out_date': b.check_out_date.isoformat() if b.check_out_date else None,
            'total_price': b.total_price,
            'status': b.status,
            'created_at': b.created_at.isoformat() if b.created_at else None
        } for b in bookings], 200
    

class AccommodationBookingByID(Resource):
    @jwt_required()
    def get(self, id):
        # Get user identity and role from JWT
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        booking = AccommodationBooking.query.filter_by(id=id).first()
        
        if not booking:
            return {"message": "Accommodation booking not found"}, 404
        
        # Role-based access control for viewing
        if role == 'tourist' and booking.tourist_id != current_user_id:
            return {"message": "Access denied"}, 403
        elif role == 'host':
            # Check if the booking is for their accommodation
            accommodation = Accommodation.query.get(booking.accommodation_id)
            if not accommodation or accommodation.host_id != current_user_id:
                return {"message": "Access denied"}, 403

        return {
            'id': booking.id,
            'tourist_id': booking.tourist_id,
            'accommodation_id': booking.accommodation_id,
            'check_in_date': booking.check_in_date.isoformat() if booking.check_in_date else None,
            'check_out_date': booking.check_out_date.isoformat() if booking.check_out_date else None,
            'total_price': booking.total_price,
            'status': booking.status,
            'created_at': booking.created_at.isoformat() if booking.created_at else None
        }, 200

    @jwt_required()
    def patch(self, id):
        # Get user identity and role from JWT
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        booking = AccommodationBooking.query.filter_by(id=id).first()
        if not booking:
            return {"message": "Accommodation booking not found"}, 404
        
        # Role-based access control for updating
        if role == 'tourist' and booking.tourist_id != current_user_id:
            return {"message": "Access denied"}, 403
        elif role == 'host':
            # Check if the booking is for their accommodation
            accommodation = Accommodation.query.get(booking.accommodation_id)
            if not accommodation or accommodation.host_id != current_user_id:
                return {"message": "Access denied"}, 403
        
        data = parser.parse_args()
        # Update attributes dynamically
        for key, value in data.items():
            if value is not None:
                setattr(booking, key, value)

        db.session.commit()
        return {
            'id': booking.id,
            'tourist_id': booking.tourist_id,
            'accommodation_id': booking.accommodation_id,
            'check_in_date': booking.check_in_date.isoformat() if booking.check_in_date else None,
            'check_out_date': booking.check_out_date.isoformat() if booking.check_out_date else None,
            'total_price': booking.total_price,
            'status': booking.status,
            'created_at': booking.created_at.isoformat() if booking.created_at else None
        }, 200

    @jwt_required()
    def delete(self, id):
        # Get user identity and role from JWT
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        booking = AccommodationBooking.query.filter_by(id=id).first()
        if not booking:
            return {"message": "Accommodation booking not found"}, 404
        
        # Role-based access control for deleting
        if role == 'tourist' and booking.tourist_id != current_user_id:
            return {"message": "Access denied"}, 403
        elif role == 'host':
            # Check if the booking is for their accommodation
            accommodation = Accommodation.query.get(booking.accommodation_id)
            if not accommodation or accommodation.host_id != current_user_id:
                return {"message": "Access denied"}, 403
        
        db.session.delete(booking)
        db.session.commit()
        return {"message": "Accommodation booking deleted successfully"}, 200

class HostBookingsResource(Resource):
    @jwt_required()
    def get(self):
        """Get all bookings for all accommodations owned by the host"""
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        if role != 'host':
            return {"message": "Access denied. Host access only."}, 403
        
        # Get all bookings for accommodations owned by this host
        bookings = AccommodationBooking.query.join(Accommodation).filter(
            Accommodation.host_id == current_user_id
        ).all()

        return [{
            'id': b.id,
            'tourist_id': b.tourist_id,
            'accommodation_id': b.accommodation_id,
            'check_in_date': b.check_in_date.isoformat() if b.check_in_date else None,
            'check_out_date': b.check_out_date.isoformat() if b.check_out_date else None,
            'total_price': b.total_price,
            'status': b.status,
            'created_at': b.created_at.isoformat() if b.created_at else None
        } for b in bookings], 200

class HostAccommodationBookingsResource(Resource):
    @jwt_required()
    def get(self, accommodation_id):
        """Get all bookings for a specific accommodation"""
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        if role != 'host':
            return {"message": "Access denied. Host access only."}, 403
        
        # Check if the accommodation exists and belongs to this host
        accommodation = Accommodation.query.filter_by(id=accommodation_id).first()
        if not accommodation:
            return {"message": "Accommodation not found"}, 404
        
        if accommodation.host_id != current_user_id:
            return {"message": "Access denied. You don't own this accommodation."}, 403
        
        # Get all bookings for this accommodation
        bookings = AccommodationBooking.query.filter_by(
            accommodation_id=accommodation_id
        ).all()

        return [{
            'id': b.id,
            'tourist_id': b.tourist_id,
            'accommodation_id': b.accommodation_id,
            'check_in_date': b.check_in_date.isoformat() if b.check_in_date else None,
            'check_out_date': b.check_out_date.isoformat() if b.check_out_date else None,
            'total_price': b.total_price,
            'status': b.status,
            'created_at': b.created_at.isoformat() if b.created_at else None
        } for b in bookings], 200

class DriverBookingsResource(Resource):
    @jwt_required()
    def get(self):
        """Get all bookings for all transports owned by the driver"""
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        if role != 'driver':
            return {"message": "Access denied. Driver access only."}, 403
        
        # Get all bookings for transports owned by this driver
        bookings = TransportBooking.query.join(Transport).filter(
            Transport.driver_id == current_user_id
        ).all()

        return [{
            'id': b.id,
            'tourist_id': b.tourist_id,
            'transport_id': b.transport_id,
            'travel_date': b.travel_date.isoformat() if b.travel_date else None,
            'seats_booked': b.seats_booked,
            'total_price': b.total_price,
            'status': b.status,
            'created_at': b.created_at.isoformat() if b.created_at else None
        } for b in bookings], 200

class DriverTransportBookingsResource(Resource):
    @jwt_required()
    def get(self, transport_id):
        """Get all bookings for a specific transport"""
        claims = get_jwt()
        role = claims.get("role")
        current_user_id = get_jwt_identity()
        
        if role != 'driver':
            return {"message": "Access denied. Driver access only."}, 403
        
        # Check if the transport exists and belongs to this driver
        transport = Transport.query.filter_by(id=transport_id).first()
        if not transport:
            return {"message": "Transport not found"}, 404
        
        if transport.driver_id != current_user_id:
            return {"message": "Access denied. You don't own this transport."}, 403
        
        # Get all bookings for this transport
        bookings = TransportBooking.query.filter_by(
            transport_id=transport_id
        ).all()

        return [{
            'id': b.id,
            'tourist_id': b.tourist_id,
            'transport_id': b.transport_id,
            'travel_date': b.travel_date.isoformat() if b.travel_date else None,
            'seats_booked': b.seats_booked,
            'total_price': b.total_price,
            'status': b.status,
            'created_at': b.created_at.isoformat() if b.created_at else None
        } for b in bookings], 200

#wip
