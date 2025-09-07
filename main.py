import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from dotenv import load_dotenv
import boto3

load_dotenv()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
BUCKET_NAME = os.getenv("secret_bucket")
s3 = boto3.client('s3', region_name=AWS_REGION)

def encrypt_file(file_path):
    aes_key = os.urandom(32)
    iv = os.urandom(16)
    with open(file_path, "rb") as f:
        data = f.read()
    padding_length = 16 - (len(data) % 16)
    data += bytes([padding_length]) * padding_length
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    ciphertext_with_iv = iv + ciphertext
    return aes_key, ciphertext_with_iv

def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def encrypt_aes_key(aes_key, public_key):
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None)
    )
    return encrypted_key

def decrypt_aes_key(encrypted_key, private_key):
    return private_key.decrypt(
        encrypted_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(),
                     label=None)
    )

def upload_to_s3(file_bytes, bucket_name, s3_key):
    s3.put_object(Bucket=bucket_name, Key=s3_key, Body=file_bytes)
    print(f"{s3_key} uploaded to S3 bucket {bucket_name}")

def download_from_s3(s3_key, download_path):
    s3.download_file(BUCKET_NAME, s3_key, download_path)
    print(f"{s3_key} downloaded from S3 to {download_path}")

def decrypt_file(encrypted_data, aes_key):
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    padding_length = decrypted_padded[-1]
    decrypted = decrypted_padded[:-padding_length]
    return decrypted

if __name__ == "__main__":
    sample_file = "test_files/sample.txt"
    encrypted_file_s3 = "sample_encrypted.txt"
    encrypted_aes_key_s3 = "encrypted_aes_key.bin"
    downloaded_file = "test_files/downloaded_sample.txt"
    downloaded_key_file = "test_files/downloaded_aes_key.bin"
    decrypted_file = "test_files/original_sample.txt"

    aes_key, ciphertext_with_iv = encrypt_file(sample_file)
    print(f"AES encryption done. Ciphertext length: {len(ciphertext_with_iv)}")

    private_key, public_key = generate_rsa_keys()
    print("RSA keys generated.")

    encrypted_aes_key = encrypt_aes_key(aes_key, public_key)
    print(f"AES key encrypted with RSA. Length: {len(encrypted_aes_key)}")

    upload_to_s3(ciphertext_with_iv, BUCKET_NAME, encrypted_file_s3)
    upload_to_s3(encrypted_aes_key, BUCKET_NAME, encrypted_aes_key_s3)

    download_from_s3(encrypted_file_s3, downloaded_file)
    download_from_s3(encrypted_aes_key_s3, downloaded_key_file)

    with open(downloaded_key_file, "rb") as f:
        encrypted_aes_key_from_s3 = f.read()

    with open(downloaded_file, "rb") as f:
        encrypted_file_from_s3 = f.read()

    aes_key_from_s3 = decrypt_aes_key(encrypted_aes_key_from_s3, private_key)
    original_data = decrypt_file(encrypted_file_from_s3, aes_key_from_s3)

    with open(decrypted_file, "wb") as f:
        f.write(original_data)
    print(f"File decrypted. Saved as {decrypted_file}")
