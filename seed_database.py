"""Script to seed database."""

import crud

# Add user
crud.create_user("testuser", "test@example.com", "password")

# Add pet for the user
crud.create_pet("test@example.com", "Dog", "Buddy", "USA", "California", "Los Angeles", 34.0522, -118.2437,
                "Bone", "Vegetables", "Fetch", "Bath", "Classical", "Rock", "Sunny", "Rainy",
                "Friendly", "Leo", "path/to/image")

# Print the user and pet to verify
print(crud.get_user_by_email("test@example.com"))
print(crud.get_pet("test@example.com"))
