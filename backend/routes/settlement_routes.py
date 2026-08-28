from flask import Blueprint, jsonify
from backend.models.trip import Trip
from backend.models.member import TripMember
from backend.models.expense import Expense, ExpenseShare
from backend.services.settlement_service import SettlementService
from backend.routes.auth_routes import token_required

settlement_bp = Blueprint('settlements', __name__, url_prefix='/api')

@settlement_bp.route('/trips/<int:trip_id>/settlements', methods=['GET'])
@token_required
def get_settlements(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({'message': 'Trip not found.'}), 404

    balances = SettlementService.get_trip_balances(trip_id)
    settlements = SettlementService.calculate_settlements(trip_id)

    return jsonify({
        'trip_id': trip_id,
        'trip_name': trip.name,
        'balances': balances,
        'settlements': settlements
    }), 200

@settlement_bp.route('/trips/<int:trip_id>/summary', methods=['GET'])
@token_required
def get_trip_summary(current_user, trip_id):
    summary = SettlementService.get_trip_summary(trip_id)
    if not summary:
        return jsonify({'message': 'Trip not found.'}), 404

    return jsonify(summary), 200

@settlement_bp.route('/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    # Fetch user trips
    created_trips = Trip.query.filter_by(created_by=current_user.id).all()
    member_trips = Trip.query.join(TripMember).filter(
        (TripMember.user_id == current_user.id) | (TripMember.email == current_user.email)
    ).all()

    user_trips_dict = {t.id: t for t in (created_trips + member_trips)}
    user_trips = list(user_trips_dict.values())

    total_trips = len(user_trips)
    active_trips = len(user_trips)  # all current trips

    total_system_expenses = 0.0
    user_total_paid = 0.0
    user_total_owe = 0.0
    user_total_receive = 0.0

    recent_expenses = []

    for trip in user_trips:
        balances = SettlementService.get_trip_balances(trip.id)
        
        # Find user's member account in this trip
        user_member = TripMember.query.filter(
            TripMember.trip_id == trip.id,
            ((TripMember.user_id == current_user.id) | (TripMember.email == current_user.email) | (TripMember.name == current_user.name))
        ).first()

        if user_member:
            for b in balances:
                if b['member_id'] == user_member.id:
                    user_total_paid += b['total_paid']
                    if b['balance'] < 0:
                        user_total_owe += abs(b['balance'])
                    elif b['balance'] > 0:
                        user_total_receive += b['balance']

        for e in trip.expenses:
            total_system_expenses += e.amount
            recent_expenses.append(e)

    # Sort recent trips and expenses
    user_trips.sort(key=lambda x: x.created_at, reverse=True)
    recent_expenses.sort(key=lambda x: x.created_at, reverse=True)

    return jsonify({
        'total_trips': total_trips,
        'active_trips': active_trips,
        'total_expenses_amount': round(total_system_expenses, 2),
        'user_total_paid': round(user_total_paid, 2),
        'user_total_owe': round(user_total_owe, 2),
        'user_total_receive': round(user_total_receive, 2),
        'recent_trips': [t.to_dict(include_counts=True) for t in user_trips[:5]],
        'recent_expenses': [e.to_dict() for e in recent_expenses[:5]]
    }), 200
