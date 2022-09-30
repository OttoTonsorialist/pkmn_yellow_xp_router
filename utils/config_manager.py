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

        self._success_color = raw.get(const.SUCCESS_COLOR_KEY, "#abebc6")
        self._warning_color = raw.get(const.WARNING_COLOR_KEY, "#f9e79f")
        self._failure_color = raw.get(const.FAILURE_COLOR_KEY, "#f5b7b1")
        self._divider_color = raw.get(const.DIVIDER_COLOR_KEY, "#b3b6b7")
        self._header_color = raw.get(const.HEADER_COLOR_KEY, "#f6ddcc")
        self._primary_color = raw.get(const.PRIMARY_COLOR_KEY, "#f6ddcc")
        self._secondary_color = raw.get(const.SECONDARY_COLOR_KEY, "#f6ddcc")
        self._contrast_color = raw.get(const.CONTRAST_COLOR_KEY, "white")
        self._background_color = raw.get(const.BACKGROUND_COLOR_KEY, "#f0f0f0")
    
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
    
    def set_success_color(self, new_color):
        self._success_color = new_color
        self._save()
    
    def set_warning_color(self, new_color):
        self._warning_color = new_color
        self._save()
    
    def set_failure_color(self, new_color):
        self._failure_color = new_color
        self._save()
    
    def set_divider_color(self, new_color):
        self._divider_color = new_color
        self._save()
    
    def set_header_color(self, new_color):
        self._header_color = new_color
        self._save()
    
    def set_primary_color(self, new_color):
        self._primary_color = new_color
        self._save()
    
    def set_secondary_color(self, new_color):
        self._secondary_color = new_color
        self._save()
    
    def set_contrast_color(self, new_color):
        self._contrast_color = new_color
        self._save()
    
    def set_background_color(self, new_color):
        self._contrast_color = new_color
        self._save()

    def get_success_color(self):
        return self._success_color

    def get_warning_color(self):
        return self._warning_color

    def get_failure_color(self):
        return self._failure_color

    def get_divider_color(self):
        return self._divider_color

    def get_header_color(self):
        return self._header_color

    def get_primary_color(self):
        return self._primary_color

    def get_secondary_color(self):
        return self._secondary_color

    def get_contrast_color(self):
        return self._contrast_color

    def get_background_color(self):
        return self._background_color

config = Config()