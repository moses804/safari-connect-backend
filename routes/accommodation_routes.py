from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Accommodation, User
from extensions import db

# Validation Rules

# Parser for POST requests (creating accommodations)
parser = reqparse.RequestParser()
parser.add_argument("title", type=str, required=True, help="Title is required")
parser.add_argument("description", type=str, required=True, help="Description is required")
parser.add_argument("location", type=str, required=True, help="Location is required")
parser.add_argument("price_per_night", type=float, required=True, help="Price per night is required")
parser.add_argument("capacity", type=int, required=True, help="Capacity is required")
parser.add_argument("available", type=bool)

# Parser for PATCH requests (updating existing accommodations)
update_parser = reqparse.RequestParser()
update_parser.add_argument("title", type=str)
update_parser.add_argument("description", type=str)
update_parser.add_argument("location", type=str)
update_parser.add_argument("price_per_night", type=float)
update_parser.add_argument("capacity", type=int)
update_parser.add_argument("available", type=bool)


class AccommodationResource(Resource):
    # Handling GET, id = None means it works for both accomms and accomms/5 for example
    def get(self, id=None):
        # If no ID provided return all accomms
        if id is None:
            # Get all accommodations
            accommodations = Accommodation.query.all()
            return [acc.to_dict() for acc in accommodations]
        
        # Get single accommodation
        accommodation = Accommodation.query.filter(Accommodation.id == id).first()
        if accommodation is None:
            return {"message": "Accommodation not found"}, 404
        
        return accommodation.to_dict()
    
    @jwt_required()
    def post(self):
        # Get current user from JWT token
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Check if user is a host
        if user.role != 'host':
            return {"message": "Only hosts can create accommodations"}, 403
        
        data = parser.parse_args()
        
        # Create new accommodation (using current_user_id from token)
        accommodation = Accommodation(
            host_id=current_user_id,
            title=data['title'],
            description=data['description'],
            location=data['location'],
            price_per_night=data['price_per_night'],
            capacity=data['capacity'],
            available=data.get('available', True)
        )
        db.session.add(accommodation)
        db.session.commit()
        
        return {"message": "Accommodation created successfully"}, 201
    
    @jwt_required()
    # Updates existing accommodations
    def patch(self, id):
        # Get current user from JWT
        current_user_id = get_jwt_identity()
        
        # Parse the update data (Only fields being changed)
        data = update_parser.parse_args()
        
        # Find accommodation to update
        accommodation = Accommodation.query.filter(Accommodation.id == id).first()
        if accommodation is None:
            return {"message": "Accommodation not found"}, 404
        
        # Check if user owns this accommodation
        if accommodation.host_id != current_user_id:
            return {"message": "You can only update your own accommodations"}, 403
        
        # Update fields that were provided
        for key, value in data.items():
            if value is not None:
                setattr(accommodation, key, value) # Only updates changed fields
        
        db.session.commit()
        return {"message": "Accommodation updated successfully"}
    
    @jwt_required()
    def delete(self, id):
        # Get current user from JWT
        current_user_id = get_jwt_identity()
        
        accommodation = Accommodation.query.filter(Accommodation.id == id).first()
        if accommodation is None:
            return {"message": "Accommodation not found"}, 404
        
        # Check if user owns this accommodation
        if accommodation.host_id != current_user_id:
            return {"message": "You can only delete your own accommodations"}, 403
        
        db.session.delete(accommodation)
        db.session.commit()
        return {"message": "Accommodation deleted successfully"}