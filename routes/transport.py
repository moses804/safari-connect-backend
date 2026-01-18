from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Transport, User
from extensions import db

# Validation RULES

parser = reqparse.RequestParser()
parser.add_argument("vehicle_type", type=str, required=True, help="Vehicle type is required")
parser.add_argument("price_per_day", type=float, required=True, help="Price per day is required")
parser.add_argument("total_capacity", type=int, required=True, help="Total capacity is required")
parser.add_argument("available", type=bool)  # Optional

# Parser for PATCH requests (updating transports)
update_parser = reqparse.RequestParser()
update_parser.add_argument("vehicle_type", type=str)
update_parser.add_argument("price_per_day", type=float)
update_parser.add_argument("total_capacity", type=int)
update_parser.add_argument("available", type=bool)


class TransportResource(Resource):
  def get(self, id = None):

    if id is None:
      transports = Transport.query.all()

      return [{
          'id': t.id,
          'vehicle_type': t.vehicle_type,
          'price_per_day': t.price_per_day,
          'total_capacity': t.total_capacity,
          'available': t.available,
          'driver_id': t.driver_id,
          'created_at': t.created_at.isoformat() if t.created_at else None
      } for t in transports]

    transport = Transport.query.filter(Transport.id == id).first()

    if transport is None:
      return {"message": "Transport not found"}, 404

    return {
        'id': transport.id,
        'vehicle_type': transport.vehicle_type,
        'price_per_day': transport.price_per_day,
        'total_capacity': transport.total_capacity,
        'available': transport.available,
        'driver_id': transport.driver_id,
        'created_at': transport.created_at.isoformat() if transport.created_at else None
    }
  
  @jwt_required()
  def post(self):
    # Get current user from JWT token
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Check if user is a driver
    if user.role != 'driver':
        return {"message": "Only drivers can create transports"}, 403
    
    # Validates incoming data
    data = parser.parse_args()

    transport = Transport(
        driver_id=current_user_id,
        vehicle_type=data['vehicle_type'],
        price_per_day=data['price_per_day'],
        total_capacity=data['total_capacity'],
        available=data.get('available', True)
    )
    db.session.add(transport)
    db.session.commit()

    return {"message": "Transport created successfully"}, 201
  
  @jwt_required()
  # PATCH METHOD
  def patch(self, id):
    # Get current user from JWT
    current_user_id = get_jwt_identity()
    
    data = update_parser.parse_args()

    transport = Transport.query.filter(Transport.id == id).first()

    if transport is None:
      return {"message":"Transport not found"}, 404
    
    # Check if user owns this transport
    if transport.driver_id != current_user_id:
        return {"message": "You can only update your own transports"}, 403
    
    # updates only provided fields
    for key, value in data.items():
      if value is not None:
        setattr(transport, key, value)

    db.session.commit()
    return {"message": "transport updated successfully"}
  
  @jwt_required()
  # DELETE METHOD
  def delete(self, id):
      # Get current user from JWT
      current_user_id = get_jwt_identity()
      
      transport = Transport.query.filter(Transport.id == id).first()

      if transport is None:
            return {"message": "Transport not found"}, 404
      
      # Check if user owns this transport
      if transport.driver_id != current_user_id:
          return {"message": "You can only delete your own transports"}, 403

      db.session.delete(transport)
      db.session.commit()
        
      return {"message": "Transport deleted successfully"}