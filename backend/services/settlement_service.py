from backend.models.trip import Trip
from backend.models.member import TripMember
from backend.models.expense import Expense, ExpenseShare
from collections import defaultdict

class SettlementService:
    @staticmethod
    def get_trip_balances(trip_id):
        """
        Calculates individual member stats: total paid, total share, net balance.
        """
        members = TripMember.query.filter_by(trip_id=trip_id).all()
        expenses = Expense.query.filter_by(trip_id=trip_id).all()

        member_stats = {}
        for m in members:
            member_stats[m.id] = {
                'member_id': m.id,
                'member_name': m.name,
                'email': m.email or '',
                'user_id': m.user_id,
                'total_paid': 0.0,
                'total_share': 0.0,
                'balance': 0.0
            }

        # Sum paid amounts
        for e in expenses:
            if e.paid_by_member_id in member_stats:
                member_stats[e.paid_by_member_id]['total_paid'] += float(e.amount)

            # Sum share amounts
            for share in e.shares:
                if share.member_id in member_stats:
                    member_stats[share.member_id]['total_share'] += float(share.share_amount)

        # Compute net balances
        balances = []
        for m_id, stats in member_stats.items():
            stats['total_paid'] = round(stats['total_paid'], 2)
            stats['total_share'] = round(stats['total_share'], 2)
            stats['balance'] = round(stats['total_paid'] - stats['total_share'], 2)
            balances.append(stats)

        return balances

    @staticmethod
    def calculate_settlements(trip_id):
        """
        Greedy Debt Simplification algorithm.
        Returns a list of minimal transactions required to settle all balances.
        """
        balances = SettlementService.get_trip_balances(trip_id)

        debtors = []   # members owing money (balance < 0)
        creditors = [] # members receiving money (balance > 0)

        for b in balances:
            bal = b['balance']
            if bal < -0.01:
                debtors.append({
                    'id': b['member_id'],
                    'name': b['member_name'],
                    'amount': abs(bal)
                })
            elif bal > 0.01:
                creditors.append({
                    'id': b['member_id'],
                    'name': b['member_name'],
                    'amount': bal
                })

        settlements = []

        while debtors and creditors:
            # Sort to match largest debtor with largest creditor
            debtors.sort(key=lambda x: x['amount'], reverse=True)
            creditors.sort(key=lambda x: x['amount'], reverse=True)

            d = debtors[0]
            c = creditors[0]

            settle_amount = min(d['amount'], c['amount'])
            settle_amount = round(settle_amount, 2)

            if settle_amount > 0:
                settlements.append({
                    'from_member_id': d['id'],
                    'from_member_name': d['name'],
                    'to_member_id': c['id'],
                    'to_member_name': c['name'],
                    'amount': settle_amount
                })

            d['amount'] = round(d['amount'] - settle_amount, 2)
            c['amount'] = round(c['amount'] - settle_amount, 2)

            if d['amount'] <= 0.01:
                debtors.pop(0)
            if c['amount'] <= 0.01:
                creditors.pop(0)

        return settlements

    @staticmethod
    def get_trip_summary(trip_id):
        """
        Generates full summary report for a trip, including charts data by category.
        """
        trip = Trip.query.get(trip_id)
        if not trip:
            return None

        expenses = Expense.query.filter_by(trip_id=trip_id).all()
        members = TripMember.query.filter_by(trip_id=trip_id).all()
        balances = SettlementService.get_trip_balances(trip_id)
        settlements = SettlementService.calculate_settlements(trip_id)

        total_expense_amount = sum(e.amount for e in expenses)

        # Expense breakdown by category
        category_totals = defaultdict(float)
        for e in expenses:
            category_totals[e.category] += e.amount

        category_breakdown = [
            {'category': cat, 'amount': round(amt, 2)}
            for cat, amt in category_totals.items()
        ]

        return {
            'trip': trip.to_dict(),
            'total_members': len(members),
            'total_expenses_count': len(expenses),
            'total_expense_amount': round(total_expense_amount, 2),
            'member_balances': balances,
            'settlements': settlements,
            'category_breakdown': category_breakdown
        }
