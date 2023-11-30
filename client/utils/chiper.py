"""Module for working with encryption on the server"""


from cryptography.fernet import Fernet
import pickle


class Chiper:
    """Class for key-based data encryption and decryption"""
    def __init__(self, key):
        self.key = Fernet(key)
        self.str_key = key

    def encrypt(self, data):
        """Encrypt some data"""
        return self.key.encrypt(pickle.dumps(data))

    def decrypt(self, data):
        """Decrypt some data"""
        return pickle.loads(self.key.decrypt(data))
