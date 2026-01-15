from flask_restful import reqparse
from daatetime import datetime


parser=reqparse.RequestParser()
parser.add_argument(  'check_in_date',
    type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
    required=True,
    help='check_in_date required (format: YYYY-MM-DD)'
)

parser.add_argument(  'check_out_date',
    type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
    required=True,
    help='check_out_date required (format: YYYY-MM-DD)'
)

parser.add_argument(
    'total_price',
    type=float,
    required=True,
    help='total_price required and must be a float'
)

parser.add_argument(
    'status',
    type=str,
    choices=('pending', 'confirmed', 'cancelled'),
    default='pending',
    help='status must be one of: pending, confirmed, cancelled'
)

parser.add_argument(
    'tourist_id',
    type=int,
    required=True,
    help='tourist_id required and must be an integer'
)


#Trnsport booking parser

transport_parser=reqparse.RequestParser()
transport_parser.add_argument(  'travel_date',
    type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
    required=True,
    help='travel_date required (format: YYYY-MM-DD)'
)

transport_parser.add_argument(
    'total_price',
    type=float,
    required=True,
    help='total_price required and must be a float'
)

transport_parser.add_argument(
    'seats_booked',
    type=int,
    required=True,
    help='seats_booked required and must be an integer'
)   

transport_parser.add_argument(
    'status',
    type=str,
    choices=('pending', 'confirmed', 'cancelled'),
    default='pending',
    help='status must be one of: pending, confirmed, cancelled'
)   

transport_parser.add_argument(
    'tourist_id',
    type=int,
    required=True,
    help='tourist_id required and must be an integer'
)   



