"""The module is needed to work with program settings"""


import json
import os
from getpass import getuser


class Settings:
    """The Settings class allows you to save and retrieve user settings"""
    def __init__(self):
        # Шлях до файлу налаштуваннь
        self.settings_folder_path = os.path.join(
            '/', 'Users', getuser(),
            '.achat')

        self.settings_file_path = os.path.join(
            self.settings_folder_path, 'settings.json')

    def get_settings(self):
        """
        Get settings
        Returns a dict with settings
        """
        with open(self.settings_file_path) as stf:
            return json.load(stf)

    def load_settings(self, obj):
        """Load settings to the settings file"""
        # If the settings folder does not exist, create it
        if not os.path.exists(self.settings_folder_path):
            os.mkdir(self.settings_folder_path)

        # If the settings file does not already exist, it is created
        if not os.path.exists(self.settings_file_path):
            with open(self.settings_file_path, 'x') as stf: stf.close()

        with open(self.settings_file_path, 'w') as stf:
            json.dump(obj, stf, indent=4)
