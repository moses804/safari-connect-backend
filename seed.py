# seed.py
"""
Seed SafariConnect database with test data.
Run: pipenv run python seed.py
"""

from app import app
from extensions import db, bcrypt
from models import User, Accommodation, Transport, AccommodationBooking, TransportBooking
from datetime import date

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("🌱 Seeding SafariConnect database...")
        
        # 1. Create Users
        alice_host = User(
            name="Alice Mwangi",
            email="alice@host.com",
            phone_number="0722123456",
            role="host"
        )
        alice_host.set_password("hostpass123")
        
        john_tourist = User(
            name="John Kamau", 
            email="john@tourist.com",
            phone_number="0711987654",
            role="tourist"
        )
        john_tourist.set_password("tourist123")
        
        mike_driver = User(
            name="Mike Omondi",
            email="mike@driver.com",
            phone_number="0700876543", 
            role="driver"
        )
        mike_driver.set_password("driverpass123")
        
        db.session.add_all([alice_host, john_tourist, mike_driver])
        db.session.commit()
        
        print(f"👥 Users created:")
        print(f"  - Host: {alice_host.email} / hostpass123")
        print(f"  - Tourist: {john_tourist.email} / tourist123")
        print(f"  - Driver: {mike_driver.email} / driverpass123")
        
        # 2. Create Accommodations (Host: Alice)
        nairobi_lodge = Accommodation(
            title="Nairobi Safari Lodge",
            description="Luxury lodge near Nairobi National Park", 
            location="Nairobi, Kenya",
            price_per_night=75.0,
            capacity=4,
            host_id=alice_host.id
        )
        
        mombasa_beach = Accommodation(
            title="Mombasa Beach Resort",
            description="Oceanfront resort with private beach access",
            location="Mombasa, Kenya",
            price_per_night=120.0,
            capacity=6,
            host_id=alice_host.id
        )
        
        db.session.add_all([nairobi_lodge, mombasa_beach])
        db.session.commit()
        
        print(f"🏨 Accommodations created by Alice:")
        print(f"  - {nairobi_lodge.title} (${nairobi_lodge.price_per_night}/night)")
        print(f"  - {mombasa_beach.title} (${mombasa_beach.price_per_night}/night)")
        
        # 3. Create Transports (Driver: Mike)
        safari_jeep = Transport(
            driver_id=mike_driver.id,
            vehicle_type="Safari Jeep",
            price_per_day=150.0,
            total_capacity=6
        )
        
        coaster_bus = Transport(
            driver_id=mike_driver.id,
            vehicle_type="Coaster Bus",
            price_per_day=300.0,
            total_capacity=20
        )
        
        db.session.add_all([safari_jeep, coaster_bus])
        db.session.commit()
        
        print(f"🚙 Transports created by Mike:")
        print(f"  - {safari_jeep.vehicle_type} (${safari_jeep.price_per_day}/day, {safari_jeep.total_capacity} seats)")
        print(f"  - {coaster_bus.vehicle_type} (${coaster_bus.price_per_day}/day, {coaster_bus.total_capacity} seats)")
        
        # 4. Create Sample Bookings (Tourist: John)
        nairobi_booking = AccommodationBooking(
            tourist_id=john_tourist.id,
            accommodation_id=nairobi_lodge.id,
            check_in_date=date(2026, 1, 15),
            check_out_date=date(2026, 1, 18),
            total_price=225.0,  # 3 nights × $75
            status="confirmed"
        )
        
        mombasa_booking = AccommodationBooking(
            tourist_id=john_tourist.id,
            accommodation_id=mombasa_beach.id,
            check_in_date=date(2026, 2, 1),
            check_out_date=date(2026, 2, 5),
            total_price=480.0,  # 4 nights × $120
            status="pending"
        )
        
        jeep_booking = TransportBooking(
            tourist_id=john_tourist.id,
            transport_id=safari_jeep.id,
            travel_date=date(2026, 1, 16),
            seats_booked=4,
            total_price=600.0,  # 4 seats × $150
            status="confirmed"
        )
        
        db.session.add_all([nairobi_booking, mombasa_booking, jeep_booking])
        db.session.commit()
        
        print("\n✅ SEED COMPLETE! Database ready for testing.")
        print("\n🧪 Test login command:")
        print("curl -X POST http://localhost:5000/api/auth/login \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -d '{\"email\":\"john@tourist.com\",\"password\":\"tourist123\"}'")
        
        print("\n📊 Final Counts:")
        print(f"Users: {User.query.count()}")
        print(f"Accommodations: {Accommodation.query.count()}")
        print(f"Transports: {Transport.query.count()}")
        print(f"Accom Bookings: {AccommodationBooking.query.count()}")
        print(f"Transport Bookings: {TransportBooking.query.count()}")

if __name__ == "__main__":
    seed_data()
