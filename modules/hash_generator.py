from werkzeug.security import generate_password_hash

print(generate_password_hash("test@1234", method="pbkdf2:sha256"))
