import pytest

bcrypt = pytest.importorskip("bcrypt")
if not hasattr(bcrypt, "__about__") or "__version__" not in bcrypt.__about__:
    pytest.skip(
        "bcrypt package lacks metadata required by passlib; install bcrypt<4.0",
        allow_module_level=True,
    )

from app.core.security import get_password_hash, verify_password


def test_password_hash_roundtrip():  # noqa: PT019
    """Ensure the hashing context works with a compatible bcrypt backend."""

    password = "hunter2"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
