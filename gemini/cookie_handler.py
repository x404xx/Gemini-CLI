import json
import os
from textwrap import dedent
from typing import Dict

from dotenv import load_dotenv

from .utils import SysOS


class GeminiCookies:
    CONFIG_FILE = "gemini_cookies.json"
    MISSING_CONFIG = """
    ⚠️  Could not find (Secure-1PSID, Secure-1PSIDTS) in environment variables or configuration.
    ⚠️  Please choose one of the following options:
        [1] Manually enter (Secure-1PSID, Secure-1PSIDTS)
        [2] Exit
    """

    @staticmethod
    def _user_choice() -> Dict[str, str]:
        while True:
            user_choice = input("Enter your choice: ")
            if user_choice == "2":
                SysOS.exit_program()
            elif user_choice == "1":
                return {
                    "Secure-1PSID": input("Enter __Secure-1PSID cookie: "),
                    "Secure-1PSIDTS": input("Enter __Secure-1PSIDTS cookie: "),
                }
            else:
                print("📛 Wrong input! Please check your value!")

    @classmethod
    def _save_config(cls, config: Dict[str, str]):
        with open(cls.CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)
        print(f'\n"{cls.CONFIG_FILE}" file has been created successfully.\n')

    @classmethod
    def _load_config(cls) -> Dict[str, str]:
        try:
            with open(cls.CONFIG_FILE, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @classmethod
    def _prompt_user_choice(cls) -> Dict[str, str]:
        print(dedent(cls.MISSING_CONFIG))
        return cls._user_choice()

    @classmethod
    def _set_gemini_cookies(cls, secure_1PSID: str, secure_1PSIDTS: str):
        cls._save_config(
            config={"Secure-1PSID": secure_1PSID, "Secure-1PSIDTS": secure_1PSIDTS}
        )

    @classmethod
    def _get_gemini_cookies(cls, args_1psid: str, args_1psidts: str):
        load_dotenv()
        secure_1PSID = os.getenv("Secure-1PSID")
        secure_1PSIDTS = os.getenv("Secure-1PSIDTS")

        if not secure_1PSID and not secure_1PSIDTS:
            if args_1psid and args_1psidts:
                secure_1PSID = args_1psid
                secure_1PSIDTS = args_1psidts
            else:
                config = cls._prompt_user_choice()
                secure_1PSID = config["Secure-1PSID"]
                secure_1PSIDTS = config["Secure-1PSIDTS"]
            cls._set_gemini_cookies(secure_1PSID, secure_1PSIDTS)

        return secure_1PSID, secure_1PSIDTS

    @classmethod
    def get_configuration(cls, args_1psid: str, args_1psidts: str):
        config = cls._load_config()
        secure_1PSID = config.get("Secure-1PSID")
        secure_1PSIDTS = config.get("Secure-1PSIDTS")

        if not secure_1PSID and not secure_1PSIDTS:
            secure_1PSID, secure_1PSIDTS = cls._get_gemini_cookies(
                args_1psid, args_1psidts
            )

        config["Secure-1PSID"] = secure_1PSID
        config["Secure-1PSIDTS"] = secure_1PSIDTS
        return config
