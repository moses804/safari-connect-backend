# TODO: Role-based views in booking_routes.py

## TransportBookingResource

- [x] Add @jwt_required() to POST method (already present)
- [x] Add @jwt_required() to GET method
- [x] Implement role-based filtering for GET:
  - tourist → their own bookings only
  - driver → bookings for their transport only
  - host → access denied or all bookings

## TransportBookingByID

- [x] Add @jwt_required() to GET method
- [x] Add @jwt_required() to PATCH method
- [x] Add @jwt_required() to DELETE method
- [x] Implement ownership/role validation for PATCH/DELETE

## AccommodationBookingResource

- [x] Add @jwt_required() to POST method (already present)
- [x] Add @jwt_required() to GET method
- [x] Implement role-based filtering for GET:
  - tourist → their own bookings only
  - host → bookings for their accommodations only
- [x] Fix logic bug - remove early return in POST

## AccommodationBookingByID

- [x] Add @jwt_required() to GET method
- [x] Add @jwt_required() to PATCH method
- [x] Add @jwt_required() to DELETE method
- [x] Implement ownership/role validation for PATCH/DELETE

## Schema Fixes

- [x] Fix typo in booking_schema.py: "daatetime" → "datetime"
