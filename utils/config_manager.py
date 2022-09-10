import json

from utils.constants import const

class Config:
    def __init__(self):
        try:
            with open(const.CONFIG_PATH, 'r') as f:
                raw = json.load(f)
        except Exception as e:
            raw = {}
        
        self._route_one_path = raw.get(const.CONFIG_ROUTE_ONE_PATH, "")
        self._window_geometry = raw.get(const.CONFIG_WINDOW_GEOMETRY, "")
    
    def _save(self):
        with open(const.CONFIG_PATH, 'w') as f:
            json.dump({
                const.CONFIG_ROUTE_ONE_PATH: self._route_one_path,
                const.CONFIG_WINDOW_GEOMETRY: self._window_geometry,
            }, f)
    
    def set_route_one_path(self, new_path):
        self._route_one_path = new_path
        self._save()

    def get_route_one_path(self):
        return self._route_one_path
    
    def set_window_geometry(self, new_geometry):
        if new_geometry != self._window_geometry:
            self._window_geometry = new_geometry
            self._save()

    def get_window_geometry(self):
        return self._window_geometry

config = Config()