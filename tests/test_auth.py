from src.auth import hash_password, verify_password

def test_hash_and_verify():
    pw = 'S3cret!'
    hashed = hash_password(pw)
    assert verify_password(pw, hashed)
