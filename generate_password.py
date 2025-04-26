from werkzeug.security import generate_password_hash

password = '123456'
hash = generate_password_hash(password, method='pbkdf2:sha256')
print(f"Password hash for '{password}': {hash}") 