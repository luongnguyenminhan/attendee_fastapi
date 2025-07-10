"""
Email utility functions for user account flows.
TODO: Implement actual email sending logic (SMTP, SendGrid, etc.)
"""
from fastapi import BackgroundTasks

def send_password_reset_email(email: str, reset_code: str, background_tasks: BackgroundTasks = None):
    # TODO: Implement actual email sending logic
    print(f"[TODO] Send password reset email to {email} with code {reset_code}")


def send_verification_email(email: str, verification_code: str, background_tasks: BackgroundTasks = None):
    # TODO: Implement actual email sending logic
    print(f"[TODO] Send verification email to {email} with code {verification_code}")
