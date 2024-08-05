from firebase import db
from datetime import datetime
from random import sample

# ------ CREATE ------ #
def create_user(username, email, password):
    """Create and return a new user."""
    user_data = {
        'username': username,
        'email': email,
        'password': password
    }
    db.collection('users').document(email).set(user_data)
    return user_data


def create_user_inventory(user_email):
    """Create user's initial inventory (3 random items from database)."""
    all_items = [doc.to_dict() for doc in db.collection('items').stream()]
    items = sample(all_items, k=3)
    user_ref = db.collection('users').document(user_email)
    user_ref.update({'items': items})
    return items


def create_pet(user_id, species_name, name, country, region, city, lat, lon,
               food_fave, food_least, activity_fave, activity_least, music_fave,
               music_least, weather_fave, weather_least, personality, astro_sign,
               species_img_path):
    """Create and return a new pet."""
    pet_data = {
        'user_id': user_id,
        'species_name': species_name,
        'name': name,
        'country': country,
        'region': region,
        'city': city,
        'lat': lat,
        'lon': lon,
        'food_fave': food_fave,
        'food_least': food_least,
        'activity_fave': activity_fave,
        'activity_least': activity_least,
        'music_fave': music_fave,
        'music_least': music_least,
        'weather_fave': weather_fave,
        'weather_least': weather_least,
        'personality': personality,
        'astro_sign': astro_sign,
        'species_img_path': species_img_path,
        'energy': 5,
        'happiness': 5,
        'last_fed': datetime.now(),
        'last_played': datetime.now()
    }
    db.collection('pets').document(user_id).set(pet_data)
    return pet_data


def create_item(item_name, description):
    """Create and return a new item."""
    item_data = {'item_name': item_name, 'description': description}
    db.collection('items').add(item_data)
    return item_data


# ------ RETRIEVE ------ #
def get_user_by_id(user_id):
    """Retrieve and return an existing user by user_id."""
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    return user.to_dict() if user.exists else None


def get_user_by_username(username):
    """Retrieve and return an existing user by username."""
    users = db.collection('users').where('username', '==', username).stream()
    for user in users:
        return user.to_dict()
    return None


def get_user_by_email(email):
    """Retrieve and return an existing user by email."""
    user_ref = db.collection('users').document(email)
    user = user_ref.get()
    return user.to_dict() if user.exists else None


def get_pet(user_id):
    """Retrieve a user's existing pet by user_id."""
    pet_ref = db.collection('pets').document(user_id)
    pet = pet_ref.get()
    return pet.to_dict() if pet.exists else None


def get_item(item_name):
    """Retrieve an item by its name."""
    items = db.collection('items').where('item_name', '==', item_name).stream()
    for item in items:
        return item.to_dict()
    return None


def get_user_items(user_id):
    """Retrieve all of a user's items."""
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    return user.to_dict().get('items', []) if user.exists else []


# ------ UPDATE ------ #
def update_pet_stats(user_id, current_energy, current_happiness):
    """Update current pet's energy and happiness stats."""
    pet_ref = db.collection('pets').document(user_id)
    pet_ref.update({
        'energy': current_energy,
        'happiness': current_happiness
    })


def update_pet_attr(user_id, attr, new_value):
    """Update an attribute for the current user's pet."""
    pet_ref = db.collection('pets').document(user_id)
    pet_ref.update({attr: new_value})
    pet = pet_ref.get()
    return pet.to_dict() if pet.exists else None


def add_item_to_user(user_id, item_name=None):
    """Connect an item to a user. If no item provided, randomly select one."""
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    if user.exists:
        user_data = user.to_dict()
        if len(user_data.get('items', [])) >= 3:
            return "error"
        if not item_name:
            items = [doc.to_dict() for doc in db.collection('items').stream()]
            available_items = [item for item in items if item not in user_data.get('items', [])]
            item = choice(available_items)
        else:
            item = get_item(item_name)
        user_data['items'].append(item)
        user_ref.update({'items': user_data['items']})
        return "success"
    return "error"


def remove_item_from_user(user_id, item_name):
    """Remove an item from a user."""
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    if user.exists:
        user_data = user.to_dict()
        user_data['items'] = [item for item in user_data.get('items', []) if item['item_name'] != item_name]
        user_ref.update({'items': user_data['items']})
        return "success"
    return "error"


# ------ DELETE ------ #
def delete_user(user_id):
    """Delete current user."""
    user_ref = db.collection('users').document(user_id)
    user_ref.delete()


def delete_pet(user_id):
    """Delete a user's existing pet."""
    pet_ref = db.collection('pets').document(user_id)
    pet_ref.delete()
