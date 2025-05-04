from fastapi import Header, HTTPException
from fastapi.requests import Request
import os

os_provider = os.name

class UnauthorizedException(HTTPException):
    """Custom exception for unauthorized access"""
    def __init__(self):
        super().__init__(status_code=403, detail="Invalid or missing device token")

secret = os.getenv("SECRET_DEVICE_TOKEN")

if not secret:
    if (os_provider == 'posix'):
        with open("./config/test.key", "r") as f:
            SECRET_DEVICE_TOKEN = f.read()
    elif (os_provider == 'nt'):
        with open("./config/test.key", "r") as f:
            SECRET_DEVICE_TOKEN = f.read()

    if not SECRET_DEVICE_TOKEN:
        exit("No secret device token found, contact the provider!")
    
    secret = SECRET_DEVICE_TOKEN
    os.environ["SECRET_DEVICE_TOKEN"] = SECRET_DEVICE_TOKEN

def verify_device_token(request: Request):
    secret_device_token = request.cookies.get("SECRET_DEVICE_TOKEN")
    if (secret_device_token != secret) or (not secret_device_token):
        raise UnauthorizedException()
    
