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
    #fetch by id
    def get_by_id(self,id):
        data = TransportBooking.query.filter_by(id==id).first()
        if not data:
            return {"message": "Transport booking not found"}, 404
        return data.to_dict(), 200
    





    
