"""
UNIT TESTS — Security functions (no DB, no HTTP)
Tests: password hashing, JWT token creation and decoding
"""
import pytest
from jose import jwt
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings


class TestPasswordHashing:

    def test_hash_is_not_plaintext(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"

    def test_correct_password_verifies(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_empty_string_hashes(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True

    def test_two_hashes_of_same_password_differ(self):
        # bcrypt generates random salt each time
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2

    def test_hash_length_is_reasonable(self):
        hashed = hash_password("test")
        assert len(hashed) > 20


class TestJWTToken:

    def test_token_is_string(self):
        token = create_access_token({"user_id": 1, "role": "user"})
        assert isinstance(token, str)

    def test_token_contains_user_id(self):
        token = create_access_token({"user_id": 42, "role": "user"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["user_id"] == 42

    def test_token_contains_role(self):
        token = create_access_token({"user_id": 1, "role": "admin"})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["role"] == "admin"

    def test_token_has_expiry(self):
        token = create_access_token({"user_id": 1})
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload

    def test_token_invalid_with_wrong_secret(self):
        from jose import JWTError
        token = create_access_token({"user_id": 1})
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong_secret", algorithms=[settings.ALGORITHM])