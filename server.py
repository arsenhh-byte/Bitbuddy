"""Server for virtual pet app."""

from multiprocessing.dummy import active_children
from flask import (Flask, render_template, request,
                   flash, session, redirect, jsonify)
from model import connect_to_db, db
import crud
import helper
from data.create_attributes import (ACTIVITY)
from random import sample
from jinja2 import StrictUndefined
import requests
import os
from craiyon import Craiyon
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("/Users/arsen/Downloads/virtual-pet-app-main2/petwebapp-17697-firebase-adminsdk-dtu50-c4ff27a6f0.json")
    firebase_admin.initialize_app(cred)

# Initialize Firestore DB
db_firestore = firestore.client()

# Create Flask app
app = Flask(__name__)
# Create secret_key (required for session object)
app.secret_key = os.environ["FLASK_APP_KEY"]
# Throw error for undefined variables
app.jinja_env.undefined = StrictUndefined



# ------------------------------------ #


@app.route('/')
def show_homepage():
    """Show homepage."""

    # Check if user is logged in. If yes, redirect to pet page.
    if helper.check_for_login():
        return redirect('/user/pet')
    else:
        return render_template("index.html")

@app.route('/user/create', methods=['POST'])
def create_user():
    """Create new user. Checks if user with provided email or username already exists."""
    user_data = request.json
    username = user_data["username"]
    email = user_data["email"]
    password = user_data["password"]
    password2 = user_data["password2"]

    valid_account = helper.check_new_account(email, username, password, password2)

    if valid_account["status"]:
        user_ref = db_firestore.collection('users').document()
        user_ref.set({
            'username': username,
            'email': email,
            'password': password  # Make sure to hash passwords in a real application
        })

    return jsonify(valid_account)


@app.route('/user/login', methods=['POST'])
def login():
    """Log user in."""
    user_data = request.json
    username = user_data["username"]
    password = user_data["password"]

    valid_account = helper.check_login(username, password)

    if valid_account["status"]:
        users_ref = db_firestore.collection('users')
        query = users_ref.where('username', '==', username).where('password', '==', password).stream()

        for user in query:
            session["current_user_id"] = user.id
            session["current_username"] = user.to_dict()["username"]
            break

    return jsonify(valid_account)

@app.route("/user/logout", methods=["POST"])
def logout():
    """Log user out."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    if session.get("current_pet"):
        current_stats = request.json
        current_energy = current_stats["currentEnergy"]
        current_happiness = current_stats["currentHappiness"]
        crud.update_pet_stats(session["current_user_id"], current_energy, current_happiness)

    session.pop("current_pet", None)
    session.pop("current_user_id", None)
    session.pop("current_username", None)
    msg = "You are now logged out."

    return jsonify({"message": msg})

@app.route("/user/delete")
def delete_user():
    """Delete current user's account."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    msg = "Your account has been deleted."

    if session.get("current_pet"):
        crud.delete_pet(session["current_user_id"])
        msg = "Your account has been deleted and your pet has been released into the wild."

    db_firestore.collection('users').document(session["current_user_id"]).delete()
    session.pop("current_pet", None)
    session.pop("current_user_id", None)
    session.pop("current_username", None)

    return jsonify({"message": msg})

@app.route('/user/pet')
def view_pet():
    """Take user to main app page."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400
    return render_template('pet.html')

@app.route("/user/pet/info")
def get_user_info():
    """Get current user's pet information from database."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    pet = session.get("current_pet", None)
    return jsonify(pet)

@app.route("/pet/new")
def generate_rand_pet():
    """Generate a random pet."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    pet = helper.generate_pet()
    return jsonify(pet)

@app.route("/user/pet/new", methods=["POST"])
def adopt_pet():
    """Create pet in database and assign to user."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    pet_data = request.json
    pet_data["user_id"] = session["current_user_id"]
    pet_data["species_name"] = pet_data["species_name"].title()

    # Extract all required fields
    user_id = session["current_user_id"]
    species_name = pet_data.get("species_name") # Prickly Bunny
    name = pet_data.get("name")
    country = pet_data.get("country")
    region = pet_data.get("region")
    city = pet_data.get("city")
    lat = pet_data.get("lat")
    lon = pet_data.get("lon")
    food_fave = pet_data.get("food_fave")
    food_least = pet_data.get("food_least")
    activity_fave = pet_data.get("activity_fave")
    activity_least = pet_data.get("activity_least")
    music_fave = pet_data.get("music_fave")
    music_least = pet_data.get("music_least")
    weather_fave = pet_data.get("weather_fave")
    weather_least = pet_data.get("weather_least")
    personality = pet_data.get("personality")
    astro_sign = pet_data.get("astro_sign")
    
    formatted_species_name = species_name.lower().replace(" ", "-")

    # Fetch the premade species image path
    species_img_dir = "/Users/arsen/Downloads/virtual-pet-app-main2/static/images/premade-species"
    species_img_path = os.path.join(species_img_dir, f"{formatted_species_name}.jpg")

    # Ensure species_img_path exists
    if not os.path.exists(species_img_path):
        return jsonify({"error": "Species image not found"}), 400

    # Call the create_pet function with all required arguments
    crud.create_pet(
        user_id, species_name, name, country, region, city, lat, lon,
        food_fave, food_least, activity_fave, activity_least,
        music_fave, music_least, weather_fave, weather_least,
        personality, astro_sign, species_img_path 
    )

    return jsonify({"success": "Pet adopted successfully"}), 200
@app.route("/user/pet/custom", methods=["POST"])
def create_custom_pet():
    """Create a custom pet species."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    pet_prompt = request.json
    pet_prompt_array = list(pet_prompt.values())
    pet_prompt_array.append("cute cartoon high resolution 4k")
    pet_prompt_str = ' '.join(pet_prompt_array)
    user_id = session["current_user_id"]
    helper.generate_craiyon_img(pet_prompt_str, user_id)
    species_img_path = f"/static/images/custom-pets/{user_id}.jpg"

    session["current_pet"] = crud.update_pet_attr(user_id, "species_img_path", species_img_path)
    
    return jsonify(session["current_pet"])

@app.route("/user/pet/rename", methods=["POST"])
def rename_user_pet():
    """Rename current user's pet."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    new_name = request.json
    session["current_pet"] = crud.update_pet_attr(session["current_user_id"], "name", new_name)

    return jsonify(session["current_pet"])

@app.route("/user/pet/delete")
def delete_user_pet():
    """Delete current user's pet."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    crud.delete_pet(session["current_user_id"])
    db.session.commit()
    session["current_pet"] = None

    return jsonify("Your pet has been released into the wild.")

@app.route("/pet/play")
def get_activities():
    """Randomly pick 3 activities and return a dictionary with their associated point value and the pet's response."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    activities = sample(ACTIVITY, k=3)
    results = helper.evaluate_interaction(session["current_pet"], activities, "activity")

    return jsonify(results)

@app.route("/pet/feed")
def get_food():
    """Get user's item inventory and return a dictionary with associated point value and pet response for each item."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    foods = crud.get_user_items(session["current_user_id"])
    results = helper.evaluate_interaction(session["current_pet"], foods, "food")

    return jsonify(results)

@app.route("/user/inventory/update", methods=["POST"])
def update_inventory():
    """Update user's inventory by removing a food item and adding a new one."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    food = request.json
    crud.remove_item_from_user(session["current_user_id"], food)
    crud.add_item_to_user(session["current_user_id"])
    db.session.commit()

    return jsonify("complete")

@app.route("/user/location")
def get_user_loc():
    """Use the user's IP address to get information about their location. Makes API request to ip-api.com"""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    url = "http://ip-api.com/json/?fields=status,country,regionName,city,zip,lat,lon,timezone,query"
    res = requests.get(url)
    user_data = res.json()

    if user_data["status"] == "fail":
        error_msg = user_data["message"]
        return jsonify({"error": error_msg}), 500

    return jsonify(user_data)

@app.route("/user/location/mock")
def mock_get_user_loc():
    """Mock version of get_user_loc() for testing."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    user_data = {
        "country": "United States",
        "regionName": "California",
        "city": "Oakland",
        "lat": 37.7994978,
        "lon": -122.2613965,
        "status": "success",
        "message": "invalid query"
    }

    if user_data["status"] == "fail":
        error_msg = user_data["message"]
        return jsonify({"error": error_msg}), 500

    return jsonify(user_data)

@app.route("/user/weather", methods=["POST"])

@app.route("/user/weather", methods=["POST"])
def get_current_weather():
    """Get current weather at the pet's location."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    location = request.json
    lat = location["lat"]
    lon = location["lon"]

    OWM_KEY = os.environ["OWM_API_KEY"]

    url = "https://api.openweathermap.org/data/2.5/weather"
    payload = {
        "lat": lat,
        "lon": lon,
        "units": "imperial",
        "appid": OWM_KEY,
    }

    res = requests.get(url, params=payload)

    if not res.ok:
        return jsonify({"error": "Weather API request failed.", "status_code": res.status_code}), res.status_code

    weather_data = res.json()
    weather_data_overview = weather_data["weather"][0]

    temp = round(weather_data["main"]["temp"])
    condition_code = weather_data_overview["id"]
    weather_type = weather_data_overview["main"]
    weather_description = weather_data_overview["description"]
    owm_icon_id = weather_data_overview["icon"]

    current_weather = {
        "tempF": temp,
        "tempC": round(helper.convert_F_to_C(temp)),
        "conditionCode": condition_code,
        "type": weather_type,
        "description": weather_description,
        "owmIconID": owm_icon_id,
    }

    return jsonify(current_weather)

@app.route("/user/weather/mock", methods=["POST"])
def mock_get_current_weather():
    """Mock version of get_current_weather() for testing."""
    if not helper.check_for_login():
        return jsonify({"error": "User not logged in"}), 400

    temp = 71.83

    current_weather = {
        'tempF': round(temp),
        "tempC": round(helper.convert_F_to_C(temp)),
        'conditionCode': 802,
        'type': 'Clouds',
        'description': 'scattered clouds',
        'owmIconID': '03d',
    }

    return jsonify(current_weather)

if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True)
