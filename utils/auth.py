from cryptography.fernet import Fernet

# Generate a key and instantiate a Fernet instance
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_user_id(user_id):
    # Ensure user_id is bytes
    user_id_bytes = str(user_id).encode()
    encrypted_text = cipher_suite.encrypt(user_id_bytes)
    return encrypted_text.decode()

def decrypt_user_id(encrypted_user_id):
    decrypted_text = cipher_suite.decrypt(encrypted_user_id.encode())
    return int(decrypted_text.decode())