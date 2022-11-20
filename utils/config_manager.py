import json
import os

from utils.constants import const
from utils import io_utils

class Config:
    DEFAULT_SUCCESS = "#abebc6"
    DEFAULT_WARNING = "#f9e79f"
    DEFAULT_FAILURE = "#f5b7b1"
    DEFAULT_DIVIDER = "#b3b6b7"
    DEFAULT_HEADER = "#f6ddcc"
    DEFAULT_PRIMARY = "#d4e6f1"
    DEFAULT_SECONDARY = "#f0f3f4"
    DEFAULT_CONTRAST = "white"
    DEFAULT_BACKGROUND = "#f0f0f0"
    DEFAULT_TEXT_COLOR = "black"
    DEFAULT_FONT_NAME = "Segoe UI"
    def __init__(self):
        try:
            with open(const.GLOBAL_CONFIG_FILE, 'r') as f:
                raw = json.load(f)
        except Exception as e:
            raw = {}
        
        self._route_one_path = raw.get(const.CONFIG_ROUTE_ONE_PATH, "")
        self._window_geometry = raw.get(const.CONFIG_WINDOW_GEOMETRY, "")
        self._user_data_dir = raw.get(const.USER_LOCATION_DATA_KEY, io_utils.get_default_user_data_dir())
        const.config_user_data_dir(self._user_data_dir)

        self._success_color = raw.get(const.SUCCESS_COLOR_KEY, self.DEFAULT_SUCCESS)
        self._warning_color = raw.get(const.WARNING_COLOR_KEY, self.DEFAULT_WARNING)
        self._failure_color = raw.get(const.FAILURE_COLOR_KEY, self.DEFAULT_FAILURE)
        self._divider_color = raw.get(const.DIVIDER_COLOR_KEY, self.DEFAULT_DIVIDER)
        self._header_color = raw.get(const.HEADER_COLOR_KEY, self.DEFAULT_HEADER)
        self._primary_color = raw.get(const.PRIMARY_COLOR_KEY, self.DEFAULT_PRIMARY)
        self._secondary_color = raw.get(const.SECONDARY_COLOR_KEY, self.DEFAULT_SECONDARY)
        self._contrast_color = raw.get(const.CONTRAST_COLOR_KEY, self.DEFAULT_CONTRAST)
        self._background_color = raw.get(const.BACKGROUND_COLOR_KEY, self.DEFAULT_BACKGROUND)
        self._text_color = raw.get(const.TEXT_COLOR_KEY, self.DEFAULT_TEXT_COLOR)

        self._custom_font_name = raw.get(const.CUSTOM_FONT_NAME_KEY, self.DEFAULT_FONT_NAME)
    
    def _save(self):
        if not os.path.exists(const.GLOBAL_CONFIG_DIR):
            os.makedirs(const.GLOBAL_CONFIG_DIR)

        with open(const.GLOBAL_CONFIG_FILE, 'w') as f:
            json.dump({
                const.CONFIG_ROUTE_ONE_PATH: self._route_one_path,
                const.CONFIG_WINDOW_GEOMETRY: self._window_geometry,
                const.USER_LOCATION_DATA_KEY: self._user_data_dir,
                const.SUCCESS_COLOR_KEY: self._success_color,
                const.WARNING_COLOR_KEY: self._warning_color,
                const.FAILURE_COLOR_KEY: self._failure_color,
                const.DIVIDER_COLOR_KEY: self._divider_color,
                const.HEADER_COLOR_KEY: self._header_color,
                const.PRIMARY_COLOR_KEY: self._primary_color,
                const.SECONDARY_COLOR_KEY: self._secondary_color,
                const.CONTRAST_COLOR_KEY: self._contrast_color,
                const.BACKGROUND_COLOR_KEY: self._background_color,
                const.TEXT_COLOR_KEY: self._text_color,
                const.CUSTOM_FONT_NAME_KEY: self._custom_font_name,
            }, f, indent=4)
    
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
    
    def get_user_data_dir(self):
        return self._user_data_dir
    
    def set_user_data_dir(self, new_dir):
        self._user_data_dir = new_dir
        const.config_user_data_dir(new_dir)
        self._save()
    
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
        self._background_color = new_color
        self._save()

    def set_text_color(self, new_color):
        self._text_color = new_color
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
    
    def get_text_color(self):
        return self._text_color
    
    def reset_all_colors(self):
        self._success_color = self.DEFAULT_SUCCESS
        self._warning_color = self.DEFAULT_WARNING
        self._failure_color = self.DEFAULT_FAILURE
        self._divider_color = self.DEFAULT_DIVIDER
        self._header_color = self.DEFAULT_HEADER
        self._primary_color = self.DEFAULT_PRIMARY
        self._secondary_color = self.DEFAULT_SECONDARY
        self._contrast_color = self.DEFAULT_CONTRAST
        self._background_color = self.DEFAULT_BACKGROUND
        self._text_color = self.DEFAULT_TEXT_COLOR
        self._save()
    
    def set_custom_font_name(self, new_name):
        self._custom_font_name = new_name
        self._save()
    
    def get_custom_font_name(self):
        return self._custom_font_name

config = Config()