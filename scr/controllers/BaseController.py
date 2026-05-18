from helpers.config import get_settings, Settings
import os
import string
import random


class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.files_dir = os.path.join(self.base_dir, "../assets/files")

    def generate_random_string(self, length: int = 12):
        # This method generates a random string of a specified length using lowercase letters and digits.
        # It is useful for creating unique identifiers, such as filenames or project IDs, to avoid conflicts and ensure uniqueness in the application.
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
