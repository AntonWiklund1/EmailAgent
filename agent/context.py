from dataclasses import dataclass

@dataclass
class UserInfo:
    user_id: str
    user_email: str
    original_input: str
    abort_response: bool = False