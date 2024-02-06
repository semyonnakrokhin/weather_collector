import configparser
import os
from datetime import datetime
from pprint import pprint
from typing import Dict, List, Literal


class IniSettings(Dict):
    def __new__(cls, ini_file: str, nested_delimiter: str = "__", *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        instance._ini_file = ini_file
        instance._nested_delimiter = nested_delimiter
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(self.parse_config_ini())

    def parse_config_ini(self):
        config = configparser.ConfigParser()
        config.read(self._ini_file)

        parsed_config = {}
        for section in config.sections():
            parsed_config[section] = {}
            for option in config.options(section):
                self.__parse_option(
                    current_dict=parsed_config[section],
                    keys=option.split(self._nested_delimiter),
                    value=config.get(section, option),
                )

        return parsed_config

    def __parse_option(self, current_dict: Dict, keys: List[str], value: str):
        if len(keys) == 1:
            current_dict[keys[0]] = value if ", " not in value else value.split(", ")
        else:
            key = keys.pop(0)
            if key not in current_dict:
                current_dict[key] = {}
            self.__parse_option(current_dict[key], keys, value)


class IniConfigSettings(IniSettings):
    def __init__(
        self,
        ini_file: str,
        root_dir: str,
        nested_delimiter: str = "__",
        *args,
        **kwargs,
    ):
        super().__init__(ini_file, nested_delimiter, *args, **kwargs)

        self["repositories"]["json_repo"]["filepath"] = self._get_filepath(
            directory=self["repositories"]["json_repo"]["filepath"],
            root_dir=root_dir,
            extension="json",
        )

        self["repositories"]["text_repo"]["filepath"] = self._get_filepath(
            directory=self["repositories"]["text_repo"]["filepath"],
            root_dir=root_dir,
            extension="txt",
        )

    @staticmethod
    def _get_filepath(
        directory: str, root_dir: str, extension: Literal["txt", "json"]
    ) -> str:
        filename = f"meteo_{int(datetime.now().timestamp() * 1e6)}.{extension}"
        return os.path.join(root_dir, directory, filename)


if __name__ == "__main__":
    ROOT_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
    )
    config_filepath = os.path.join(ROOT_DIR, "config.ini")
    config_ini_settings = IniConfigSettings(ini_file=config_filepath, root_dir=ROOT_DIR)

    pprint(config_ini_settings)
