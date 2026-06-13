from helpers.config import get_settings, Settings
import os
import string
import random


# BaseController serves as a foundational class for other controllers in the application, providing common functionalities and configurations.
# It initializes application settings and defines utility methods that can be used across different controllers, such as
class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        # base_dir is set to the directory of the current file, and files_dir is set to a specific path within the assets directory where uploaded files will be stored.
        # This setup allows for organized storage of files and easy access to application settings across all controllers that inherit from BaseController.
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.files_dir = os.path.join(self.base_dir, "../assets/files")

        self.database_dir = os.path.join(self.base_dir, "../assets/database")

    def generate_random_string(self, length: int = 12):
        # This method generates a random string of a specified length using lowercase letters and digits.
        # It is useful for creating unique identifiers, such as filenames or project IDs, to avoid conflicts and ensure uniqueness in the application.
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def get_database_path(self, db_name: str):
        database_path = os.path.join(self.database_dir, db_name)

        if not os.path.exists(database_path):
            os.makedirs(database_path)
        return database_path
