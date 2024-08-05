"""Models for virtual pet app (User, Pet, Item, UserItem) using Firebase."""
import firebase_admin

from datetime import datetime
from firebase_admin import credentials, firestore

# Initialize the Firebase app
cred = credentials.Certificate('petwebapp-17697-firebase-adminsdk-dtu50-c4ff27a6f0.json')
firebase_admin.initialize_app(cred)


# Initialize Firestore DB (make sure this is only initialized once)
db = firestore.client()

class User:
    """A user."""

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def create_user(username, email, password):
        user = User(username, email, password)
        user_ref = db.collection('users').document(email)
        user_ref.set(user.__dict__)
        return user

    @staticmethod
    def get_user_by_email(email):
        user_ref = db.collection('users').document(email)
        return user_ref.get().to_dict()

class Pet:
    """A pet."""

    def __init__(self, user_id, species_name, name):
        self.user_id = user_id
        self.species_name = species_name
        self.name = name
        self.energy = 5
        self.happiness = 5
        self.last_fed = datetime.now()
        self.last_played = datetime.now()

    @staticmethod
    def create_pet(user_id, species_name, name):
        pet = Pet(user_id, species_name, name)
        pet_ref = db.collection('pets').document(user_id)
        pet_ref.set(pet.__dict__)
        return pet

    @staticmethod
    def get_pet_by_user_id(user_id):
        pet_ref = db.collection('pets').document(user_id)
        return pet_ref.get().to_dict()

def connect_to_db(app):
    """Connect to Firestore database."""
    print("Connected to Firestore database!")
