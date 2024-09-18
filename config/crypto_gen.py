from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
import hashlib


def generate_server_key():
    # Private keys defined
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Public Keys defined
    public_key = private_key.public_key()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    try:
        with open ("private_key.pem", "wb") as private_key_file:
            private_key_file.write(pem_private)
        with open ("public_key.pem", "wb") as public_key_file:
            public_key_file.write(pem_public)
        print("Keys have succesfully been created")

    except PermissionError:
        print("No write permissions on the folder")

    except Exception as e:
        print("Something went wrong")


    with open ("private_key.pem", "rb") as original_file:
        key_data = original_file.read()
        with open ("confirm.txt", "wb") as confirm_file:
            confirm_file.write(key_data)


    confirm_private_file_hash = get_file_hash("confirm.txt", hash_algorithm="sha256")
    print(f"Sha256 hash for private key: {confirm_private_file_hash}")
    return confirm_private_file_hash


# Confirm that keys have not been modified
def confirm_no_tampering(confirm_private_file_hash, original_file):
    original_file_hash = get_file_hash(original_file, hash_algorithm="sha256")
    copy_file_hash = get_file_hash(confirm_private_file_hash)
    if copy_file_hash != original_file_hash:
        print("Keys do not match")
        return False
    else:
        print("All seems good")
        return True


def rsa_encrypt(message_to_encrypt, public_key):
    encrypted_message = public_key.encrypt(
        message_to_encrypt.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_message
    

def rsa_decrypt(message_to_decrypt, private_key):
    decrypted_message = private_key.decrypt(
        message_to_decrypt,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_message.decode('utf-8')


def load_public_key(public_key_path):
    with open(public_key_path, "rb") as public_key_file:
        public_key = serialization.load_pem_public_key(public_key_file.read())
    return public_key


def load_private_key(private_key_path):
    with open(private_key_path, "rb") as private_key_file:
        private_key = serialization.load_pem_private_key(
            private_key_file.read(),
            password = None
        )
    return private_key

# Define the aes key for the beacon
    def generate_aes_key():
        pass

def get_file_hash(file_path, hash_algorithm="sha256"):
    hash_function = hashlib.new(hash_algorithm)

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_function.update(chunk)

    return hash_function.hexdigest()