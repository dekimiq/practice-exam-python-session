from datetime import datetime
import re

class User:
    def __init__(self, username, email, role) -> None:
        self.id = None
        self.username = username
        self.email = email
        self.role = role
        self.registration_date = datetime.now()

    def _is_valid_email(self, email) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def update_info(self, username=None, email=None, role=None) -> None:
        if username:
            self.username = username
        if email and self._is_valid_email(email):
            self.email = email
        if role:
            self.role = role

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'registration_date': self.registration_date.isoformat() if isinstance(self.registration_date, datetime) else self.registration_date
        }
