import firebase_admin
from firebase_admin import credentials
import os

cred_path = "/etc/secrets/firebase_key.json"

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
