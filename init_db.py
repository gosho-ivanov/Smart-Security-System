"""
Run this once to create all tables and seed sample data.
Usage: python init_db.py
"""
from security_system import create_app
from security_system.extensions import db
from security_system.models import User, Door, PinCode, PinCodeDoor, Fingerprint, FingerprintDoor
from datetime import datetime, date

app = create_app()

with app.app_context():
    db.create_all()
    print("✓ Tables created.")

    # Seed admin user
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            name='John Doe',
            username='johndoe',
            email='admin@example.com',
            role='administrator',
        )
        admin.set_password('Admin1234!')
        db.session.add(admin)

        jane = User(name='Jane Smith',  username='janesmith',  email='jane@example.com', role='user')
        jane.set_password('User1234!')
        peter = User(name='Peter Jones', username='peterjones', email='peter@example.com', role='user', is_active=False)
        peter.set_password('User1234!')

        db.session.add_all([jane, peter])
        db.session.flush()

        # Seed doors
        doors = [
            Door(name='Main Entrance', location='Front of House',  method_pin=True,  method_fp=True),
            Door(name='Back Door',     location='Rear of House',   method_pin=True,  method_fp=True),
            Door(name='Garage Door',   location='Garage',          method_pin=True,  method_fp=False),
            Door(name='Side Gate',     location='East Side Yard',  method_pin=False, method_fp=True),
        ]
        db.session.add_all(doors)
        db.session.flush()

        # Seed PIN codes
        pin1 = PinCode(user_id=admin.id, expires_at=datetime(2024, 12, 31))
        pin1.set_pin('1234')
        pin2 = PinCode(user_id=jane.id,  expires_at=datetime(2025, 6, 15))
        pin2.set_pin('5678')
        db.session.add_all([pin1, pin2])
        db.session.flush()

        db.session.add_all([
            PinCodeDoor(pin_code_id=pin1.id, door_id=doors[0].id),
            PinCodeDoor(pin_code_id=pin1.id, door_id=doors[1].id),
            PinCodeDoor(pin_code_id=pin2.id, door_id=doors[0].id),
        ])

        # Seed fingerprints
        fp1 = Fingerprint(user_id=admin.id, template_ref='slot_1')
        fp2 = Fingerprint(user_id=jane.id,  template_ref='slot_2')
        db.session.add_all([fp1, fp2])
        db.session.flush()

        db.session.add_all([
            FingerprintDoor(fingerprint_id=fp1.id, door_id=doors[0].id),
            FingerprintDoor(fingerprint_id=fp1.id, door_id=doors[1].id),
            FingerprintDoor(fingerprint_id=fp2.id, door_id=doors[0].id),
        ])

        db.session.commit()
        print("✓ Sample data seeded.")
        print("\nAdmin credentials:")
        print("  Email:    admin@example.com")
        print("  Password: Admin1234!")
    else:
        print("✓ Database already seeded.")
