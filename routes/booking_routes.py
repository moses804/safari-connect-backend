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
        
        return [booking.to_dict() for booking in bookings], 200
        
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
        
        return booking.to_dict(), 200
    
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
        return booking.to_dict(), 200
    
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
        
        return [booking.to_dict() for booking in bookings], 200
    

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
        
        return booking.to_dict(), 200

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
        return booking.to_dict(), 200

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

#wip