from backend.database.db import db
from backend.models.expense import Expense, ExpenseShare
from backend.models.member import TripMember

class ExpenseService:
    @staticmethod
    def create_expense(trip_id, title, amount, category, paid_by_member_id, expense_date, shared_member_ids, notes=""):
        """
        Creates a new expense and automatically calculates and stores equal shares among shared members.
        """
        if amount <= 0:
            raise ValueError("Expense amount must be greater than zero.")

        if not shared_member_ids or len(shared_member_ids) == 0:
            raise ValueError("Expense must be shared by at least one member.")

        # Verify paid_by_member belongs to this trip
        paid_by = TripMember.query.filter_by(id=paid_by_member_id, trip_id=trip_id).first()
        if not paid_by:
            raise ValueError("Paid by member does not belong to this trip.")

        # Verify all shared_members belong to this trip
        valid_members = TripMember.query.filter(
            TripMember.id.in_(shared_member_ids),
            TripMember.trip_id == trip_id
        ).all()

        if len(valid_members) != len(set(shared_member_ids)):
            raise ValueError("One or more selected shared members are invalid for this trip.")

        expense = Expense(
            trip_id=trip_id,
            title=title.strip(),
            amount=float(amount),
            category=category,
            paid_by_member_id=paid_by_member_id,
            expense_date=expense_date,
            notes=notes.strip() if notes else ""
        )

        db.session.add(expense)
        db.session.flush()  # Generate expense.id

        # Calculate equal split
        num_members = len(shared_member_ids)
        share_per_person = round(float(amount) / num_members, 2)

        # Distribute remaining cents if rounding difference exists
        total_calculated = share_per_person * num_members
        remainder = round(float(amount) - total_calculated, 2)

        for idx, member_id in enumerate(shared_member_ids):
            allocated_share = share_per_person
            if idx == 0 and remainder != 0:
                allocated_share = round(allocated_share + remainder, 2)

            expense_share = ExpenseShare(
                expense_id=expense.id,
                member_id=member_id,
                share_amount=allocated_share
            )
            db.session.add(expense_share)

        db.session.commit()
        return expense

    @staticmethod
    def update_expense(expense_id, trip_id, title, amount, category, paid_by_member_id, expense_date, shared_member_ids, notes=""):
        """
        Updates an existing expense and recalculates shares.
        """
        expense = Expense.query.filter_by(id=expense_id, trip_id=trip_id).first()
        if not expense:
            raise ValueError("Expense not found.")

        if amount <= 0:
            raise ValueError("Expense amount must be greater than zero.")

        if not shared_member_ids or len(shared_member_ids) == 0:
            raise ValueError("Expense must be shared by at least one member.")

        # Delete existing shares
        ExpenseShare.query.filter_by(expense_id=expense_id).delete()

        expense.title = title.strip()
        expense.amount = float(amount)
        expense.category = category
        expense.paid_by_member_id = paid_by_member_id
        expense.expense_date = expense_date
        expense.notes = notes.strip() if notes else ""

        num_members = len(shared_member_ids)
        share_per_person = round(float(amount) / num_members, 2)
        total_calculated = share_per_person * num_members
        remainder = round(float(amount) - total_calculated, 2)

        for idx, member_id in enumerate(shared_member_ids):
            allocated_share = share_per_person
            if idx == 0 and remainder != 0:
                allocated_share = round(allocated_share + remainder, 2)

            expense_share = ExpenseShare(
                expense_id=expense.id,
                member_id=member_id,
                share_amount=allocated_share
            )
            db.session.add(expense_share)

        db.session.commit()
        return expense
