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