from flask import Blueprint, request, jsonify
from backend.database.db import db
from backend.models.trip import Trip
from backend.models.expense import Expense
from backend.services.expense_service import ExpenseService
from backend.routes.auth_routes import token_required

expense_bp = Blueprint('expenses', __name__, url_prefix='/api')

@expense_bp.route('/trips/<int:trip_id>/expenses', methods=['GET'])
@token_required
def get_trip_expenses(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({'message': 'Trip not found.'}), 404

    category_filter = request.args.get('category', '').strip()
    search_query = request.args.get('search', '').strip().lower()
    sort_by = request.args.get('sort', 'date_desc').strip()

    query = Expense.query.filter_by(trip_id=trip_id)

    if category_filter and category_filter != 'All':
        query = query.filter_by(category=category_filter)

    expenses = query.all()

    if search_query:
        expenses = [
            e for e in expenses 
            if search_query in e.title.lower() or search_query in (e.notes or '').lower() or search_query in e.paid_by_member.name.lower()
        ]

    # Sorting
    if sort_by == 'amount_desc':
        expenses.sort(key=lambda x: x.amount, reverse=True)
    elif sort_by == 'amount_asc':
        expenses.sort(key=lambda x: x.amount)
    elif sort_by == 'date_asc':
        expenses.sort(key=lambda x: x.expense_date)
    else:  # date_desc default
        expenses.sort(key=lambda x: x.expense_date, reverse=True)

    return jsonify({
        'expenses': [e.to_dict() for e in expenses]
    }), 200

@expense_bp.route('/trips/<int:trip_id>/expenses', methods=['POST'])
@token_required
def create_expense(current_user, trip_id):
    trip = Trip.query.get(trip_id)
    if not trip:
        return jsonify({'message': 'Trip not found.'}), 404

    data = request.get_json() or {}

    title = data.get('title', '').strip()
    amount = data.get('amount', 0)
    category = data.get('category', 'Other')
    paid_by_member_id = data.get('paid_by_member_id')
    expense_date = data.get('expense_date', '').strip()
    shared_member_ids = data.get('shared_member_ids', [])
    notes = data.get('notes', '').strip()

    if not title or not amount or not paid_by_member_id or not expense_date:
        return jsonify({'message': 'Title, amount, paid by member, and date are required.'}), 400

    try:
        expense = ExpenseService.create_expense(
            trip_id=trip_id,
            title=title,
            amount=float(amount),
            category=category,
            paid_by_member_id=int(paid_by_member_id),
            expense_date=expense_date,
            shared_member_ids=[int(m_id) for m_id in shared_member_ids],
            notes=notes
        )
        return jsonify({
            'message': 'Expense added successfully!',
            'expense': expense.to_dict()
        }), 201
    except ValueError as err:
        return jsonify({'message': str(err)}), 400
    except Exception as err:
        return jsonify({'message': f'Failed to create expense: {str(err)}'}), 500

@expense_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@token_required
def update_expense(current_user, expense_id):
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({'message': 'Expense not found.'}), 404

    data = request.get_json() or {}

    title = data.get('title', expense.title).strip()
    amount = data.get('amount', expense.amount)
    category = data.get('category', expense.category)
    paid_by_member_id = data.get('paid_by_member_id', expense.paid_by_member_id)
    expense_date = data.get('expense_date', expense.expense_date).strip()
    shared_member_ids = data.get('shared_member_ids', [s.member_id for s in expense.shares])
    notes = data.get('notes', expense.notes).strip()

    try:
        updated_expense = ExpenseService.update_expense(
            expense_id=expense_id,
            trip_id=expense.trip_id,
            title=title,
            amount=float(amount),
            category=category,
            paid_by_member_id=int(paid_by_member_id),
            expense_date=expense_date,
            shared_member_ids=[int(m_id) for m_id in shared_member_ids],
            notes=notes
        )
        return jsonify({
            'message': 'Expense updated successfully!',
            'expense': updated_expense.to_dict()
        }), 200
    except ValueError as err:
        return jsonify({'message': str(err)}), 400
    except Exception as err:
        return jsonify({'message': f'Failed to update expense: {str(err)}'}), 500

@expense_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@token_required
def delete_expense(current_user, expense_id):
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify({'message': 'Expense not found.'}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({'message': 'Expense deleted successfully!'}), 200
