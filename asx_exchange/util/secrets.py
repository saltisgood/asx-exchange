import json

class Secrets:
    @staticmethod
    def from_file(file='secrets.json'):
        with open(file, 'r') as f:
            return Secrets(json.load(f))

    def __init__(self, obj: dict):
        self._obj = obj
        
    def get_str(self, key, default=None):
        try:
            return str(self._obj[key])
        except KeyError:
            return default
    
    def get_sub(self, key, default=None):
        try:
            return Secrets(self._obj[key])
        except KeyError:
            return default
    