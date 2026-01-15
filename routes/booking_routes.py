from flask_restful import Resource, abort
from flask import request
from schemas.booking_schema import parser, transport_parser
from models import db, AccommodationBooking, TransportBooking

class TransportBookingResource(Resource):
    def post(self):
        data = transport_parser.parse_args()

        # 1. Fetch transport capacity
        transport = TransportBooking.query.get(data['transport_id'])
        
        # 2. Calculate already booked seats for that date
        booked_seats = db.session.query(db.func.sum(TransportBooking.seats_booked)).filter(
            TransportBooking.transport_id == data['transport_id'],
            TransportBooking.travel_date == data['travel_date']
        ).scalar() or 0
        
        # 3. Check if new booking exceeds capacity
        if booked_seats + data['seats_booked'] > transport.total_capacity:
            return {"message": "Not enough seats available on this date"}, 400


        #new transport instance
        trans_inputs = TransportBooking(**data)
        #save to database
        db.session.add(trans_inputs)
        db.session.commit()
        return {
            "message": "Transport booking created successfully", 
            "booking_id": trans_inputs.id
        }, 201
    
        #fetch all
    def get(self):
        data = TransportBooking.query.all
        return [booking.to_dict() for booking in data], 200
        
class TransportBookingByID(Resource):
    #fetch by id
    def get_by_id(self,id):
        data = TransportBooking.query.filter_by(id==id).first()
        if not data:
            return {"message": "Transport booking not found"}, 404
        return data.to_dict(), 200
    
    # updating
    def patch(self, id):
        booking = TransportBooking.query.filter_by(id=id).first()
        if not booking:
            return {"message": "Transport booking not found"}, 404
        
        # Parse arguments
        data = transport_parser.parse_args()
        for key, value in data.items():
            if value is not None:
                setattr(booking, key, value)
        
        db.session.commit()
        return booking.to_dict(), 200
    
    #deleting
    def delete(self, id):
        data = TransportBooking.query.filter_by(id=id).first()
        if not data:
            return {"message": "Transport booking not found"}, 404
        
        db.session.delete(data)
        db.session.commit()
        return {"message": "Transport booking deleted successfully"}, 200
    

class AccommodationBookingResource(Resource) :
    def post(self):
        # Parse data using your accommodation-specific parser
        data = parser.parse_args()

        #extra validation
        if data['check_out_date'] <= data['check_in_date']:
            return {"message": "check_out_date must be after check_in_date"}, 400

        # Check for overlapping bookings
        conflict = AccommodationBooking.query.filter(
            AccommodationBooking.accommodation_id == data['accommodation_id'],
            AccommodationBooking.check_in < data['check_out'],
            AccommodationBooking.check_out > data['check_in']
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

        # Fetch all records
    def get(self):
        bookings = AccommodationBooking.query.all()
        return [booking.to_dict() for booking in bookings], 200
    

class AccommodationBookingByID(Resource):
    def get(self, id):
        booking = AccommodationBooking.query.filter_by(id=id).first()
        
        if not booking:
            return {"message": "Accommodation booking not found"}, 404
        
        return booking.to_dict(), 200

    def patch(self, id):
        booking = AccommodationBooking.query.filter_by(id=id).first()
        if not booking:
            return {"message": "Accommodation booking not found"}, 404
        
        data = parser.parse_args()
        # Update attributes dynamically
        for key, value in data.items():
            if value is not None:
                setattr(booking, key, value)
        
        db.session.commit()
        return booking.to_dict(), 200

    def delete(self, id):
        booking = AccommodationBooking.query.filter_by(id=id).first()
        if not booking:
            return {"message": "Accommodation booking not found"}, 404
        
        db.session.delete(booking)
        db.session.commit()
        return {"message": "Accommodation booking deleted successfully"}, 200







    
