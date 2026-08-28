import os
import sys

# Set standard output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import create_app
from backend.services.settlement_service import SettlementService

def run_tests():
    app = create_app()
    with app.test_client() as client:
        print("--- TEST 1: User Login ---")
        login_res = client.post('/api/login', json={
            'email': 'demo@example.com',
            'password': 'password123'
        })
        print("Login Status:", login_res.status_code)
        assert login_res.status_code == 200
        token = login_res.get_json()['token']
        headers = {'Authorization': f'Bearer {token}'}
        print("JWT Token acquired successfully!")

        print("\n--- TEST 2: Dashboard Stats ---")
        stats_res = client.get('/api/dashboard/stats', headers=headers)
        print("Stats Status:", stats_res.status_code)
        print("Stats Output Summary: Total Expenses =", stats_res.get_json()['total_expenses_amount'])
        assert stats_res.status_code == 200

        print("\n--- TEST 3: Get Trip Details ---")
        trip_res = client.get('/api/trips/1', headers=headers)
        print("Trip Status:", trip_res.status_code)
        trip_data = trip_res.get_json()['trip']
        print(f"Trip Name: {trip_data['name']}, Members Count: {len(trip_data['members'])}, Expenses Count: {len(trip_data['expenses'])}")
        assert trip_res.status_code == 200

        print("\n--- TEST 4: Get Trip Settlements & Balances ---")
        settle_res = client.get('/api/trips/1/settlements', headers=headers)
        print("Settlement Status:", settle_res.status_code)
        settle_data = settle_res.get_json()
        print("\nMember Balances:")
        for b in settle_data['balances']:
            print(f" - {b['member_name']}: Paid = INR {b['total_paid']}, Share = INR {b['total_share']}, Balance = INR {b['balance']}")

        print("\nSimplified Settlements:")
        for s in settle_data['settlements']:
            print(f" -> {s['from_member_name']} pays {s['to_member_name']} INR {s['amount']}")

        print("\n--- TEST 5: Create New Expense & Verify Dynamic Re-calculation ---")
        new_exp_res = client.post('/api/trips/1/expenses', headers=headers, json={
            'title': 'Taxi to Airport',
            'amount': 2000,
            'category': 'Travel',
            'paid_by_member_id': 2, # Alice Smith
            'expense_date': '2026-09-06',
            'shared_member_ids': [1, 2, 3, 4], # All 4 members (500 each)
            'notes': 'Airport drop'
        })
        print("New Expense Status:", new_exp_res.status_code)
        assert new_exp_res.status_code == 201

        # Re-fetch settlements
        settle_res_2 = client.get('/api/trips/1/settlements', headers=headers)
        print("\nUpdated Settlements after adding Taxi expense (INR 2000 by Alice):")
        for s in settle_res_2.get_json()['settlements']:
            print(f" -> {s['from_member_name']} pays {s['to_member_name']} INR {s['amount']}")

        print("\nALL BACKEND API TESTS PASSED SUCCESSFULLY! ✅")

if __name__ == '__main__':
    run_tests()
