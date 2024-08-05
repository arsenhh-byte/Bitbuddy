"""Helper functions."""

from flask import (session)
import crud
from model import db
from random import (choice, sample, randint)
# Lists of pet attributes
from data.create_attributes import (
    SPECIES_ID, SPECIES, FOOD, ACTIVITY, MUSIC_GENRE, WEATHER, PERSONALITY,
    ASTROLOGICAL_SIGN
)
# For craiyon.py
from craiyon import Craiyon
from PIL import Image # pip install pillow
from io import BytesIO
import base64


def check_login(username, password):
    """
    Check if the provided username and password are correct.

    Arguments:
    - username (str): The username provided by the user.
    - password (str): The password provided by the user.

    Returns:
    - valid_account (dict): Information about attempted account login
        - "status" (bool): Whether account is valid (True) or not (False)
        - "msg" (str): Message for user confirming log in
        - "user_id" (int): User ID for account
        - "username" (str): Username for account
    """
    user = crud.get_user_by_username(username)
    print(user)
    print(user["password"] == password)
    if user and user["password"] == password:
        return { 
            "status": True,
            "msg": "Log in successful",
            "username": user["username"]}
    else:
        return {
            "status": False,
            "msg": "Invalid username or password.",
            "username": None
        }

def check_for_login():
    """Check if a user is currently logged in.

    Returns:
    - True or False (bool): True if user is logged in, False if not
    """

    if session.get("current_user_id"):
        return True
    else:
        return False


def check_new_account(email, username, password, password2):
    """Check whether account creation is valid.

    Checks if email is already in use, if username is already in use, and
    whether both password fields match. If no issues, creates new user account
    and logs user in. Parameters come from Create Account form.

    Arguments:
    - email (str): User-provided email
    - username (str): User-provided username
    - password (str): User-provided password
    - password2 (str): User-provided confirmation of password (must match password arg)

    Return:
    - valid_account (dict): Information about attempted account creation
        - "status" (bool): Whether account is valid (True) or not (False)
        - "msg" (str): Whether account was successfully created (and if not,
        reason for error)
        - "user_id" (int): If account was created, user ID for new account
        - "username" (str): Username for account
    """

    valid_account = {"status": False, "msg": ""}

    # Flash error if email already in use
    if crud.get_user_by_email(email) is not None:
        valid_account["msg"] = "ERROR: An account with this email already exists."

    # Flash error if username already in use
    elif crud.get_user_by_username(username) is not None:
        valid_account["msg"] = "ERROR: An account with this username already exists."

    # Flash error if passwords don't match
    elif password != password2:
        valid_account["msg"] = "ERROR: Passwords do not match."

    # Create account and add to databases
    else:
        # Create user
        user = crud.create_user(username, email, password)
        # Create user starting inventory
        crud.create_user_inventory(user)
        db.session.add(user)
        db.session.commit()
        # Get newly created User object from db
        user = crud.get_user_by_username(username)
        # Log user in
        valid_account = log_in_user(
            user, "Your account has successfully been created!")

    return valid_account

def log_in_user(user, msg):
    """
    Creates session object with keys to track user ID and username.

    Argument:
    - user (database object): User object from database
    - msg (str): Success message to display after login

    Returns:
    - valid_account (dict): Information about attempted account login
        - "status" (bool): Whether account is valid (True) or not (False)
        - "msg" (str): Message for user confirming log in
        - "user_id" (int): User ID for account
        - "username" (str): Username for account
    """
    
    try:
        session["current_user_id"] = user["user_id"]
        session["current_username"] = user["username"]
    except KeyError as e:
        return {
            "status": False,
            "msg": f"Error: Missing key {str(e)} in user object.",
            "user_id": None,
            "username": None
        }

    pet = crud.get_pet(session["current_user_id"])
    if pet:
        session["current_pet"] = pet.convert_to_dict()
    else:
        session["current_pet"] = None

    valid_account = {
        "status": True,
        "msg": msg,
        "user_id": session["current_user_id"],
        "username": session["current_username"]
    }

    return valid_account


def generate_pet():
    """Randomly generate a pet.

    Returns a dictionary of pet attributes."""

    species_type = choice(SPECIES_ID)
    species_name = SPECIES[species_type][0]
    species_img_path = SPECIES[species_type][1]
    food_fave_least = sample(FOOD, k=2)
    food_fave = food_fave_least[0]
    food_least = food_fave_least[1]
    activity_fave_least = sample(ACTIVITY, k=2)
    activity_fave = activity_fave_least[0]
    activity_least = activity_fave_least[1]
    music_fave_least = sample(MUSIC_GENRE, k=2)
    music_fave = music_fave_least[0]
    music_least = music_fave_least[1]
    weather_fave_least = sample(WEATHER, k=2)
    weather_fave = weather_fave_least[0]
    weather_least = weather_fave_least[1]
    personality = sample(PERSONALITY, k=3)
    personality = ', '.join(personality)
    astro_sign = choice(ASTROLOGICAL_SIGN)

    pet = {
        "species_name": species_name,
        "name": None,
        "country": None,
        "region": None,
        "city": None,
        "lat": None,
        "lon": None,
        "species_img_path": species_img_path,
        "food_fave": food_fave,
        "food_least": food_least,
        "activity_fave": activity_fave,
        "activity_least": activity_least,
        "music_fave": music_fave,
        "music_least": music_least,
        "weather_fave": weather_fave,
        "weather_least": weather_least,
        "personality": personality,
        "astro_sign": astro_sign,
    }

    return pet


def convert_F_to_C(temp_F):
    """Converts temperature in Fahrenheit to Celsius.

    Argument:
    - temp_F (int): Temperature in Fahrenheit

    Returns:
    - temp_C (int): Temperature in Celsius
    """

    temp_C = (temp_F - 32) / 1.8

    return temp_C


def evaluate_interaction(pet, interactions, interaction_type):
    """Evaluates user's interaction with pet.

    Arguments:
    - pet (dict): Dictionary of pet attributes
    - interactions (lst): A list of interactions
    - interaction_type (str): Interaction type (must be "food" or "activity")

    Return:
    - results (dict): Dictionary of each interaction item, which has a nested dictionary of the pet's response phrase and the interaction's value (impact on stat)
    """

    interaction_responses = {
        "activity": {
            "good": "Wow, that was so much fun! Can we do it again?",
            "bad": "Meh... I didn't really like that...",
            "neutral": "That was fun!"
        },
        "food": {
            "good": "Mmm, that was the best thing I've ever had!",
            "bad": "Yuck, I didn't like that one.",
            "neutral": "Yum, thanks for the snack!",
        }
    }

    results = {}

    for option in interactions:
        results[option] = {}
        if option == pet[f"{interaction_type}_fave"]:
            results[option]["value"] = 2
            results[option]["response"] = interaction_responses[f"{interaction_type}"]["good"]
        elif option == pet[f"{interaction_type}_least"]:
            results[option]["value"] = -1
            results[option]["response"] = interaction_responses[f"{interaction_type}"]["bad"]
        else:
            results[option]["value"] = 1
            results[option]["response"] = interaction_responses[f"{interaction_type}"]["neutral"]

    return results


def generate_craiyon_img(text_prompt, user_id):
    """Send a text prompt to Craiyon and store the first resulting image.

    Arguments:
    - text_prompt (str): Text prompt to send to Craiyon
    - user_id (int): Current user's user ID
    """
    generator = Craiyon()   # Instantiates the api wrapper
    result = generator.generate(text_prompt)
    images = result.images  # A list containing image data as base64 encoded strings

    # GET ONE RANDOM IMAGE
    idx = randint(0, 8)     # Get random # from 1-9 to use for img idx
    image = Image.open(BytesIO(base64.decodebytes(images[idx].encode("utf-8"))))
    # image.show()    # Opens image on computer
    image.save(f"static/images/custom-pets/{user_id}.jpg")   # Saves image to file path, using user_id as filename

    # LOOP THROUGH ALL 9 IMAGES
    # j = 1
    # for i in images:
    #     image = Image.open(BytesIO(base64.decodebytes(i.encode("utf-8"))))
    #     image.show()    # Opens image on computer
    #     image.save(f"generated/craiyon-test/{j}.jpg")   # Saves image to file path, with provided filename and extension
    #     j += 1
    
    
