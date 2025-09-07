# Cloud Crypto Security

A secure file storage system that uses **AES encryption** for file contents, **RSA encryption** for the AES key and **AWS S3** for cloud storage.  

This project demonstrates a complete workflow:
1. Encrypt a file locally with AES.
2. Encrypt the AES key using RSA.
3. Upload both the encrypted file and key to AWS S3.
4. Download from S3 and decrypt the file back to its original form.

---

## Project Structure

cloud-crypto-security/
├── test_files/
│ ├── sample.txt
│ ├── downloaded_sample.txt
│ ├── downloaded_aes_key.bin
│ ├── original_sample.txt
│ └── test_read.py
├── venv/
├── main.py
├── .env
├── .gitignore
└── README.md

---

## Tech Stack Used
- **Python**  
  - cryptography  
  - boto3  
  - python-dotenv  
- **AWS S3** (for file storage)


##  Features
- AES-256 file encryption (CBC mode with padding).
- RSA-2048 key pair generation.
- AES key encryption using RSA public key.
- Secure storage of encrypted files in AWS S3.
- Full cycle: **Encrypt → Upload → Download → Decrypt**.

---

##  Installation & Setup


```bash
Clone this repository:
git clone <repo-link>
cd cloud-crypto-security


Create and activate a virtual environment:
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

Install dependencies:
pip install -r requirements.txt


Environment Variables
Create a .env file in the root directory:
AWS_DEFAULT_REGION=ap-south-1
secret_bucket=your-s3-bucket-name


Make sure your AWS credentials are configured via AWS CLI:
aws configure





