"""
Script test API Backend
Chạy: python test_backend.py
"""
import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000/api"
TOKEN = None

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_response(label, status, data):
    print(f"\n[OK] {label} (Status: {status})")
    if isinstance(data, dict):
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(data)

def print_error(label, status, error):
    print(f"\n[ERROR] {label} (Status: {status})")
    print(json.dumps(error, indent=2, ensure_ascii=False))

# ============================================================
# 1. TEST AUTHENTICATION
# ============================================================
print_section("1. TEST AUTHENTICATION")

# Login
print("\n[INFO] Logging in as admin...")
url = f"{BASE_URL}/auth/login/"
data = {"username": "admin", "password": "admin123"}
response = requests.post(url, json=data)
if response.status_code in [200, 201]:
    TOKEN = response.json().get('access')
    print_response("Login", response.status_code, response.json())
else:
    print_error("Login failed", response.status_code, response.json())
    TOKEN = None

if not TOKEN:
    print("\n[ERROR] Could not get token. Exiting...")
    exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# ============================================================
# 2. TEST CREATE MASTER DATA (Districts, AgencyTypes, Units)
# ============================================================
print_section("2. TEST CREATE MASTER DATA")

# Create District
print("\n[INFO] Creating District...")
url = f"{BASE_URL}/agencies/districts/"
data = {"name": "District 1"}
response = requests.post(url, json=data, headers=HEADERS)
district_id = response.json().get('id') if response.status_code == 201 else None
print_response("Create District", response.status_code, response.json())

# Create AgencyType
print("\n[INFO] Creating AgencyType...")
url = f"{BASE_URL}/agencies/types/"
data = {"name": "Type 1", "max_debt": 10000000}
response = requests.post(url, json=data, headers=HEADERS)
agency_type_id = response.json().get('id') if response.status_code == 201 else None
print_response("Create AgencyType", response.status_code, response.json())

# Create Unit
print("\n[INFO] Creating Unit...")
url = f"{BASE_URL}/products/units/"
data = {"name": "Piece"}
response = requests.post(url, json=data, headers=HEADERS)
unit_id = response.json().get('id') if response.status_code == 201 else None
print_response("Create Unit", response.status_code, response.json())

# ============================================================
# 3. TEST CREATE AGENCY & PRODUCT
# ============================================================
print_section("3. TEST CREATE AGENCY & PRODUCT")

# Create Agency
print("\n[INFO] Creating Agency...")
url = f"{BASE_URL}/agencies/"
data = {
    "name": "Agency ABC",
    "agency_type": agency_type_id,
    "district": district_id,
    "phone": "0123456789",
    "email": "abc@example.com",
    "address": "123 Street ABC, District 1",
    "reception_date": str(date.today())
}
response = requests.post(url, json=data, headers=HEADERS)
agency_id = response.json().get('id') if response.status_code == 201 else None
print_response("Create Agency", response.status_code, response.json())

# Create Product
print("\n[INFO] Creating Product...")
url = f"{BASE_URL}/products/"
data = {
    "name": "Product A",
    "unit": unit_id,
    "price": 50000,
    "stock_quantity": 100,
    "description": "Description of product A"
}
response = requests.post(url, json=data, headers=HEADERS)
product_id = response.json().get('id') if response.status_code == 201 else None
print_response("Create Product", response.status_code, response.json())

# ============================================================
# 4. TEST GOODS RECEIPT (Nhập Kho)
# ============================================================
print_section("4. TEST GOODS RECEIPT (Import Stock)")

print("\n[INFO] Creating Goods Receipt...")
url = f"{BASE_URL}/products/receipts/"
data = {
    "receipt_date": str(date.today()),
    "note": "Import from supplier",
    "items": [
        {
            "product": product_id,
            "quantity": 50,
            "unit_price": 45000
        }
    ]
}
response = requests.post(url, json=data, headers=HEADERS)
print_response("Create Goods Receipt", response.status_code, response.json())

# Check product stock updated
print("\n[INFO] Checking product stock...")
url = f"{BASE_URL}/products/{product_id}/"
response = requests.get(url, headers=HEADERS)
print_response("Get Product", response.status_code, response.json())

# ============================================================
# 5. TEST EXPORT ORDER (Phiếu Xuất)
# ============================================================
print_section("5. TEST EXPORT ORDER (Export Order)")

print("\n[INFO] Creating Export Order...")
url = f"{BASE_URL}/orders/"
data = {
    "agency": agency_id,
    "order_date": str(date.today()),
    "note": "Customer order",
    "items": [
        {
            "product": product_id,
            "quantity": 10,
            "unit_price": 50000
        }
    ]
}
response = requests.post(url, json=data, headers=HEADERS)
order_id = response.json().get('id') if response.status_code == 201 else None
print_response("Create Export Order", response.status_code, response.json())

# Check agency debt updated
print("\n[INFO] Checking agency debt...")
url = f"{BASE_URL}/agencies/{agency_id}/debt_info/"
response = requests.get(url, headers=HEADERS)
print_response("Get Agency Debt Info", response.status_code, response.json())

# ============================================================
# 6. TEST ORDER WORKFLOW
# ============================================================
print_section("6. TEST ORDER WORKFLOW")

if order_id:
    # Confirm order
    print("\n[INFO] Confirming order...")
    url = f"{BASE_URL}/orders/{order_id}/confirm/"
    response = requests.post(url, headers=HEADERS)
    print_response("Confirm Order", response.status_code, response.json())
    
    # Ship order
    print("\n[INFO] Shipping order...")
    url = f"{BASE_URL}/orders/{order_id}/ship/"
    response = requests.post(url, headers=HEADERS)
    print_response("Ship Order", response.status_code, response.json())
    
    # Complete order
    print("\n[INFO] Completing order...")
    url = f"{BASE_URL}/orders/{order_id}/complete/"
    response = requests.post(url, headers=HEADERS)
    print_response("Complete Order", response.status_code, response.json())

# ============================================================
# 7. TEST PAYMENT
# ============================================================
print_section("7. TEST PAYMENT")

print("\n[INFO] Creating Payment...")
url = f"{BASE_URL}/payments/"
data = {
    "agency": agency_id,
    "payment_date": str(date.today()),
    "amount": 200000,
    "note": "Pay debt"
}
response = requests.post(url, json=data, headers=HEADERS)
print_response("Create Payment", response.status_code, response.json())

# Check updated debt
print("\n[INFO] Checking updated agency debt...")
url = f"{BASE_URL}/agencies/{agency_id}/debt_info/"
response = requests.get(url, headers=HEADERS)
print_response("Get Updated Debt Info", response.status_code, response.json())

# ============================================================
# 8. TEST DASHBOARD
# ============================================================
print_section("8. TEST DASHBOARD")

print("\n[INFO] Getting Dashboard Overview...")
url = f"{BASE_URL}/reports/dashboard/overview/"
response = requests.get(url, headers=HEADERS)
print_response("Dashboard Overview", response.status_code, response.json())

# ============================================================
# 9. TEST FILTERS & SEARCH
# ============================================================
print_section("9. TEST FILTERS & SEARCH")

print("\n[INFO] Searching agencies...")
url = f"{BASE_URL}/agencies/?search=ABC"
response = requests.get(url, headers=HEADERS)
print_response("Search Agencies", response.status_code, response.json())

print("\n[INFO] Filtering orders by status...")
url = f"{BASE_URL}/orders/?status=completed"
response = requests.get(url, headers=HEADERS)
print_response("Filter Orders", response.status_code, response.json())

print_section("TEST COMPLETED")
print("\n[SUCCESS] Backend API test completed!")
print("If no errors, the system is working normally.")
