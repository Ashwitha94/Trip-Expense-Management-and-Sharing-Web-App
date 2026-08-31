from backend.database.db import db
from backend.models.user import User
from backend.models.trip import Trip
from backend.models.member import TripMember
from backend.services.expense_service import ExpenseService

def seed_demo_data():
    if User.query.filter_by(email="demo@example.com").first():
        return

    print("Creating demo user...")
    demo_user = User(
        name="Ashwitha Maragoni",
        email="demo@example.com"
    )
    demo_user.set_password("password123")
    db.session.add(demo_user)
    db.session.commit()

    print("Creating sample trips...")
    trip1 = Trip(
        name="Manali Adventure Trip",
        destination="Manali, Himachal Pradesh",
        start_date="2026-09-01",
        end_date="2026-09-07",
        description="Group vacation to Manali with trekking, sports, and sightseeing.",
        image_url="images/mountains.jpg",
        created_by=demo_user.id
    )
    trip2 = Trip(
        name="Paris & Euro Tour",
        destination="Paris, France",
        start_date="2026-10-10",
        end_date="2026-10-18",
        description="Eiffel Tower, Louvre Museum, Seine River Cruise & French pastry tasting.",
        image_url="images/paris.jpg",
        created_by=demo_user.id
    )
    trip3 = Trip(
        name="Swiss Alps & Chalet Stay",
        destination="Zurich & Interlaken, Switzerland",
        start_date="2026-11-05",
        end_date="2026-11-12",
        description="Mount Titlis, Jungfraujoch, scenic cable cars & Swiss chocolates.",
        image_url="images/switzerland.jpg",
        created_by=demo_user.id
    )
    trip4 = Trip(
        name="Varanasi & Ganga Yatra",
        destination="Varanasi, Uttar Pradesh",
        start_date="2026-12-01",
        end_date="2026-12-05",
        description="Sacred Ganga Aarti, ancient temples, boat rides & spiritual retreat.",
        image_url="images/holy_places.jpg",
        created_by=demo_user.id
    )

    db.session.add_all([trip1, trip2, trip3, trip4])
    db.session.flush()

    print("Adding trip members...")
    m1_john = TripMember(trip_id=trip1.id, name="Ashwitha Maragoni", email="demo@example.com", user_id=demo_user.id)
    m1_alice = TripMember(trip_id=trip1.id, name="Alice Smith", email="alice@example.com")
    m1_bob = TripMember(trip_id=trip1.id, name="Bob Johnson", email="bob@example.com")
    m1_charlie = TripMember(trip_id=trip1.id, name="Charlie Brown", email="charlie@example.com")

    m2_john = TripMember(trip_id=trip2.id, name="Ashwitha Maragoni", email="demo@example.com", user_id=demo_user.id)
    m2_sophie = TripMember(trip_id=trip2.id, name="Sophie Martin", email="sophie@example.com")
    m2_lucas = TripMember(trip_id=trip2.id, name="Lucas Bernard", email="lucas@example.com")

    m3_john = TripMember(trip_id=trip3.id, name="Ashwitha Maragoni", email="demo@example.com", user_id=demo_user.id)
    m3_emma = TripMember(trip_id=trip3.id, name="Emma Watson", email="emma@example.com")

    m4_john = TripMember(trip_id=trip4.id, name="Ashwitha Maragoni", email="demo@example.com", user_id=demo_user.id)
    m4_raj = TripMember(trip_id=trip4.id, name="Rajesh Sharma", email="rajesh@example.com")

    db.session.add_all([m1_john, m1_alice, m1_bob, m1_charlie, m2_john, m2_sophie, m2_lucas, m3_john, m3_emma, m4_john, m4_raj])
    db.session.commit()

    print("Adding sample expenses...")
    ExpenseService.create_expense(
        trip_id=trip1.id, title="Luxury Resort Stay", amount=12000.0, category="Hotel",
        paid_by_member_id=m1_john.id, expense_date="2026-09-01",
        shared_member_ids=[m1_john.id, m1_alice.id, m1_bob.id, m1_charlie.id], notes="3 nights stay"
    )
    ExpenseService.create_expense(
        trip_id=trip2.id, title="Eiffel Tower Fast Pass", amount=15000.0, category="Entertainment",
        paid_by_member_id=m2_john.id, expense_date="2026-10-11",
        shared_member_ids=[m2_john.id, m2_sophie.id, m2_lucas.id], notes="Summit access"
    )
    ExpenseService.create_expense(
        trip_id=trip3.id, title="Swiss Alps Cable Car Express", amount=22000.0, category="Travel",
        paid_by_member_id=m3_john.id, expense_date="2026-11-06",
        shared_member_ids=[m3_john.id, m3_emma.id], notes="Titlis cable car"
    )
    ExpenseService.create_expense(
        trip_id=trip4.id, title="Special Boat Ride", amount=3500.0, category="Other",
        paid_by_member_id=m4_john.id, expense_date="2026-12-02",
        shared_member_ids=[m4_john.id, m4_raj.id], notes="Ganga Ghat boat ride"
    )
    db.session.commit()