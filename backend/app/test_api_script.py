"""
Script to test user/auth API endpoints and log results.
Usage: python test_api_script.py
"""
import requests
import json
from app.utils.dev_token_utils import get_dev_auth_token

API_BASE = "http://localhost:8000/api/v1"
LOG_FILE = "test_api_log.txt"

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def main():
    # Generate dev token (TODO: remove in production)
    email = "testuser@example.com"
    user_id = "00000000-0000-0000-0000-000000000001"
    org_id = None
    token = get_dev_auth_token(email, user_id, org_id)
    headers = {"Authorization": f"Bearer {token}"}
    log(f"Dev token: {token}")

    # Test /auth/me
    r = requests.get(f"{API_BASE}/auth/me", headers=headers)
    log(f"GET /auth/me: {r.status_code} {r.text}")

    # Test /auth/password-reset
    data = {"email": email}
    r = requests.post(f"{API_BASE}/auth/password-reset", json=data)
    log(f"POST /auth/password-reset: {r.status_code} {r.text}")

    # Test /auth/password-reset-confirm
    data = {"email": email, "reset_code": "123456", "new_password": "NewPassword123!"}
    r = requests.post(f"{API_BASE}/auth/password-reset-confirm", json=data)
    log(f"POST /auth/password-reset-confirm: {r.status_code} {r.text}")

    # Test /auth/resend-verification
    data = {"email": email}
    r = requests.post(f"{API_BASE}/auth/resend-verification", json=data)
    log(f"POST /auth/resend-verification: {r.status_code} {r.text}")

    # Test /auth/email-verify
    data = {"email": email, "verification_code": "654321"}
    r = requests.post(f"{API_BASE}/auth/email-verify", json=data)
    log(f"POST /auth/email-verify: {r.status_code} {r.text}")

    # Test /auth/logout
    r = requests.post(f"{API_BASE}/auth/logout", headers=headers)
    log(f"POST /auth/logout: {r.status_code} {r.text}")

if __name__ == "__main__":
    main()
