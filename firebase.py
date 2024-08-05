import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate('petwebapp-17697-firebase-adminsdk-dtu50-c4ff27a6f0.json') 
    default_app = firebase_admin.initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()