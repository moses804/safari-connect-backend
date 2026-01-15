from flask_restful import Resource, reqparse
from models import Transport, db


# Validation RULES

parser = reqparse.RequestParser()
parser.add_argument("driver_id", type=int, required=True, help="Driver ID is required")
parser.add_argument("vehicle_type", type=str, required=True, help="Vehicle type is required")
parser.add_argument("vehicle_name", type=str, required=True, help="Vehicle name is required")
parser.add_argument("route", type=str)  # Optional
parser.add_argument("price_per_day", type=float, required=True, help="Price per day is required")
parser.add_argument("capacity", type=int, required=True, help="Capacity is required")
parser.add_argument("features", type=str)  # Optional
parser.add_argument("image_url", type=str)  # Optional
parser.add_argument("available", type=bool)  # Optional

# Parser for PATCH requests (updating transports)
update_parser = reqparse.RequestParser()
update_parser.add_argument("vehicle_type", type=str)
update_parser.add_argument("vehicle_name", type=str)
update_parser.add_argument("route", type=str)
update_parser.add_argument("price_per_day", type=float)
update_parser.add_argument("capacity", type=int)
update_parser.add_argument("features", type=str)
update_parser.add_argument("image_url", type=str)
update_parser.add_argument("available", type=bool)


class TransportResource(Resource):
  def get(self, id = None):

    if id is None:
      transports = Transport.query.all()


      return [transport.to_dict() for transport in transports]
    
    transport = Transport.query.filter(Transport.id == id).first()

    if transport is None:
      return {"message": "Transport not found"}, 404
    

    return transport.to_dict()
  

  def post(self):
    # Validates incoming data
    data = parser.parse_args()

    transport = Transport(**data)

    db.session.commit()

    return {"message": "Transport created successfully"}, 201
  
  # PATCH METHOD


  def patch(self, id):
    
    data = update_parser.parse_args()

    transport = Transport = Transport.query.filter(Transport.id == id).first()

    if transport is None:
      return {"message":"Transport not found"}, 404
    
    # updates only provided fields

    for key, value in data.items():
      if value is not None:
        setattr(transport, key, value)


    db.session.commit()
    return {"message": "transport added successfully"}
  

  # DELETE METHOD
  def delete(self, id):
      transport = Transport.query.filter(Transport.id == id).first()

      if transport is None:
            return {"message": "Transport not found"}, 404
      

      db.session.delete(transport)
      db.session.commit()
        
      return {"message": "Transport deleted successfully"}
    

