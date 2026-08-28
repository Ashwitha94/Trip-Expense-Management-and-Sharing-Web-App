from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.models.trip import Trip
from backend.models.member import TripMember
from backend.models.expense import Expense
from backend.routes.auth_routes import token_required

trip_bp = Blueprint('trips', __name__, url_prefix='/api/trips')

@trip_bp.route('', methods=['GET'])
@token_required
def get_user_trips(current_user):
    """
    Returns trips created by the user or where the user is listed as a member.
    """
    created_trips = Trip.query.filter_by(created_by=current_user.id).all()
    
    # Also find trips where user is a member
    member_trips = Trip.query.join(TripMember).filter(
        (TripMember.user_id == current_user.id) | (TripMember.email == current_user.email)
    ).all()

    # Combine unique trips
    all_trips_dict = {t.id: t for t in (created_trips + member_trips)}
    trips_list = [t.to_dict(include_counts=True) for t in sorted(all_trips_dict.values(), key=lambda x: x.created_at, reverse=True)]

    return jsonify({'trips': trips_list}), 200

@trip_bp.route('', methods=['POST'])
@token_required
def create_trip(current_user):
    data = request.get_json() or {}

    name = data.get('name', '').strip()
    destination = data.get('destination', '').strip()
    start_date = data.get('start_date', '').strip()
    end_date = data.get('end_date', '').strip()
    description = data.get('description', '').strip()
    image_url = data.get('image_url', 'images/mountains.jpg').strip()

    if not name or not destination or not start_date or not end_date:
        return jsonify({'message': 'Trip name, destination, start date, and end date are required.'}), 400

    trip = Trip(
        name=name,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        description=description,
        image_url=image_url if image_url else 'images/mountains.jpg',
        created_by=current_user.id
    )

    db.session.add(trip)
    db.session.flush()

    # Automatically add creator as first trip member
    creator_member = TripMember(
        trip_id=trip.id,
        name=current_user.name,
        email=current_user.email,
        user_id=current_user.id
    )
    db.session.add(creator_member)

    # Optional: add initial members if provided in request
    initial_members = data.get('members', [])
    for m in initial_members:
        m_name = m.get('name', '').strip() if isinstance(m, dict) else str(m).strip()
        m_email = m.get('email', '').strip().lower() if isinstance(m, dict) else ''
        if m_name and m_name.lower() != current_user.name.lower():
            db.session.add(TripMember(
                trip_id=trip.id,
                name=m_name,
                email=m_email if m_email else None
            ))

    db.session.commit()

    return jsonify({
        'message': 'Trip created successfully!',
        'trip': trip.to_dict(include_counts=True)
    }), 201

@trip_bp.route('/<int:trip_id>', methods=['GET'])
@token_required
def get_trip_details(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({'message': 'Trip not found.'}), 404

    # Check permission
    is_creator = trip.created_by == current_user.id
    is_member = TripMember.query.filter(
        TripMember.trip_id == trip_id,
        (TripMember.user_id == current_user.id) | (TripMember.email == current_user.email)
    ).first() is not None

    if not (is_creator or is_member):
        return jsonify({'message': 'Unauthorized access to this trip.'}), 403

    members = [m.to_dict() for m in trip.members]
    expenses = [e.to_dict() for e in sorted(trip.expenses, key=lambda x: x.created_at, reverse=True)]

    result = trip.to_dict(include_counts=True)
    result['members'] = members
    result['expenses'] = expenses
    result['is_creator'] = is_creator

    return jsonify({'trip': result}), 200

@trip_bp.route('/<int:trip_id>', methods=['PUT'])
@token_required
def update_trip(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({'message': 'Trip not found.'}), 404

    if trip.created_by != current_user.id:
        return jsonify({'message': 'Only the trip creator can update trip details.'}), 403

    data = request.get_json() or {}

    trip.name = data.get('name', trip.name).strip()
    trip.destination = data.get('destination', trip.destination).strip()
    trip.start_date = data.get('start_date', trip.start_date).strip()
    trip.end_date = data.get('end_date', trip.end_date).strip()
    trip.description = data.get('description', trip.description).strip()
    trip.image_url = data.get('image_url', trip.image_url).strip()

    db.session.commit()
    return jsonify({
        'message': 'Trip updated successfully!',
        'trip': trip.to_dict(include_counts=True)
    }), 200

@trip_bp.route('/<int:trip_id>', methods=['DELETE'])
@token_required
def delete_trip(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({'message': 'Trip not found.'}), 404

    if trip.created_by != current_user.id:
        return jsonify({'message': 'Only the trip creator can delete this trip.'}), 403

    db.session.delete(trip)
    db.session.commit()
    return jsonify({'message': 'Trip deleted successfully!'}), 200

# Member Management Routes
@trip_bp.route('/<int:trip_id>/members', methods=['GET'])
@token_required
def get_trip_members(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({'message': 'Trip not found.'}), 404

    members = [m.to_dict() for m in trip.members]
    return jsonify({'members': members}), 200

@trip_bp.route('/<int:trip_id>/members', methods=['POST'])
@token_required
def add_trip_member(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({'message': 'Trip not found.'}), 404

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()

    if not name:
        return jsonify({'message': 'Member name is required.'}), 400

    # Check for duplicate member name in trip
    existing = TripMember.query.filter_by(trip_id=trip_id, name=name).first()
    if existing:
        return jsonify({'message': f'Member "{name}" is already in this trip.'}), 409

    member = TripMember(
        trip_id=trip_id,
        name=name,
        email=email if email else None
    )

    db.session.add(member)
    db.session.commit()

    return jsonify({
        'message': 'Member added successfully!',
        'member': member.to_dict()
    }), 201

@trip_bp.route('/members/<int:member_id>', methods=['DELETE'])
@token_required
def remove_trip_member(current_user, member_id):
    member = TripMember.query.get(member_id)
    if not member:
        return jsonify({'message': 'Member not found.'}), 404

    trip = Trip.query.get(member.trip_id)
    if trip.created_by != current_user.id:
        return jsonify({'message': 'Only the trip creator can remove members.'}), 403

    # Check if member has paid expenses or has shares
    expenses_paid_count = Expense.query.filter_by(paid_by_member_id=member_id).count()
    if expenses_paid_count > 0:
        return jsonify({'message': f'Cannot remove member {member.name} because they have paid expenses logged.'}), 400

    db.session.delete(member)
    db.session.commit()

    return jsonify({'message': 'Member removed successfully!'}), 200
