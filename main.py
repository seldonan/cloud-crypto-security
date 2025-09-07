# main.py
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env



import os
import boto3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# --------------------------
# AWS Setup
# --------------------------
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
BUCKET_NAME = os.getenv("secret_bucket")
s3 = boto3.client('s3', region_name=AWS_REGION)

# --------------------------
# AES Encryption
# --------------------------
def encrypt_file(file_path):
    aes_key = os.urandom(32)   # 256-bit AES key
    iv = os.urandom(16)        # 16-byte IV

    # Read file
    with open(file_path, "rb") as f:
        data = f.read()

    # Pad data to multiple of 16 bytes
    padding_length = 16 - (len(data) % 16)
    data += bytes([padding_length]) * padding_length

    # Encrypt with AES CBC
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()

    return aes_key, iv, ciphertext

# --------------------------
# RSA Key Generation & AES key encryption
# --------------------------
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key

def encrypt_aes_key(aes_key, public_key):
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_key

# --------------------------
# Upload to S3
# --------------------------
def upload_to_s3(file_bytes, bucket_name, s3_key):
    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=file_bytes)
    print(f"Uploaded {s3_key} to S3 bucket {bucket_name}")

# --------------------------
# Main Execution
# --------------------------
if __name__ == "__main__":
    # File to encrypt
    file_path = "test_files/sample.txt"

    # Step 1: Encrypt file with AES
    aes_key, iv, ciphertext = encrypt_file(file_path)
    print("AES encryption done. Ciphertext length:", len(ciphertext))

    # Step 2: Generate RSA keys
    private_key, public_key = generate_rsa_keys()
    print("RSA keys generated.")

    # Step 3: Encrypt AES key with RSA
    encrypted_aes_key = encrypt_aes_key(aes_key, public_key)
    print("AES key encrypted with RSA. Length:", len(encrypted_aes_key))

    # Step 4: Upload encrypted file and AES key to S3
    upload_to_s3(ciphertext, BUCKET_NAME, "sample_encrypted.txt")
    upload_to_s3(encrypted_aes_key, BUCKET_NAME, "sample_encrypted_key.bin")


    # Upload AES-encrypted file
upload_to_s3(ciphertext, BUCKET_NAME, "sample_encrypted.txt")

# Upload RSA-encrypted AES key
upload_to_s3(encrypted_aes_key, BUCKET_NAME, "sample_encrypted_key.bin")

print("Encrypted file and AES key uploaded to S3 successfully!")

