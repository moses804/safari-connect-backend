from flask_restful import Resource, abort
from flask import request
from schemas.booking_schema import parser, transport_parser
from models import db, AccommodationBooking, TransportBooking

class TransportBookingResource(Resource):
    def post(self):
        data = transport_parser.parse_args()
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
        

    class AccommodationBooking(Resource) :
        def post(self):
            # Parse data using your accommodation-specific parser
            data = parser.parse_args()
            
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







    
