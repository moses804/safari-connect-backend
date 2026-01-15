from flask_restful import Resource, reqparse
from models import Accommodation, db



# Validation Rules



# Parser for POST requests (creating accommodations)
parser = reqparse.RequestParser()
parser.add_argument("host_id", type=int, required=True, help="Host ID is required")
parser.add_argument("title", type=str, required=True, help="Title is required")
parser.add_argument("description", type=str, required=True, help="Description is required")
parser.add_argument("location", type=str, required=True, help="Location is required")
parser.add_argument("price_per_night", type=float, required=True, help="Price per night is required")
parser.add_argument("capacity", type=int, required=True, help="Capacity is required")

# Optional fields

parser.add_argument("amenities", type=str)
parser.add_argument("image_url", type=str)
parser.add_argument("available", type=bool)

# Parser for PATCH requests (updating existing accommodations)
update_parser = reqparse.RequestParser()
update_parser.add_argument("title", type=str)
update_parser.add_argument("description", type=str)
update_parser.add_argument("location", type=str)
update_parser.add_argument("price_per_night", type=float)
update_parser.add_argument("capacity", type=int)
update_parser.add_argument("amenities", type=str)
update_parser.add_argument("image_url", type=str)
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
    
    def post(self):
        data = parser.parse_args()
        
        # Create new accommodation
        accommodation = Accommodation(**data)
        db.session.add(accommodation)
        db.session.commit()
        
        return {"message": "Accommodation created successfully"}, 201
    

    # Updates existing accommodations
    def patch(self, id):
        # Parse the update data (Only fields being changed)
        data = update_parser.parse_args()
        
        # Find accommodation to update
        accommodation = Accommodation.query.filter(Accommodation.id == id).first()
        if accommodation is None:
            return {"message": "Accommodation not found"}, 404
        
        # Update fields that were provided
        for key, value in data.items():
            if value is not None:
                setattr(accommodation, key, value) # Only updates changed fields
        
        db.session.commit()
        return {"message": "Accommodation updated successfully"}
    
    def delete(self, id):
        accommodation = Accommodation.query.filter(Accommodation.id == id).first()
        if accommodation is None:
            return {"message": "Accommodation not found"}, 404
        
        db.session.delete(accommodation)
        db.session.commit()
        return {"message": "Accommodation deleted successfully"}