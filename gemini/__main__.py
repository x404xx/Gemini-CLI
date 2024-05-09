from argparse import ArgumentParser
from os import getenv
from pathlib import Path
from sys import stdout
from textwrap import dedent
from time import sleep

from dotenv import load_dotenv

from .api import GeminiAPI
from .cookie_handler import GeminiCookies
from .utils import Colors, SysOS

load_dotenv()


class StartGemini:
    def __init__(self, delay: float = 0.003, proxy: str = None):
        self.delay = delay
        self.proxy = proxy
        self._result()

    def _instruction(self):
        self._delay_print(
            dedent(
                """
            CLI tool for interacting with Google's Gemini chatbot (https://gemini.google.com)
               [!] PLEASE DOUBLE 'enter' TO SEND A MESSAGE.
                  - Type !clear to clear the console.
                  - Type !reset to reset the conversation.
                  - Type !exit to exit the program.
        """
            )
        )

    def _delay_print(self, words: str):
        for word in words:
            stdout.write(word)
            stdout.flush()
            sleep(self.delay)
        stdout.write("\n")

    def _get_query(self, prompt: str) -> str:
        print(prompt, end="")
        return "\n".join(iter(input, ""))

    def _handle_user_prompt(self, user_prompt: str, gemini: GeminiAPI) -> bool:
        if user_prompt == "!exit":
            return False
        elif user_prompt == "!clear":
            SysOS.clear_console()
            self._instruction()
        elif user_prompt == "!reset":
            self._reset_gemini(gemini)
            SysOS.clear_console()
            self._instruction()
        else:
            self._ask_gemini(user_prompt, gemini)
        return True

    def _reset_gemini(self, gemini: GeminiAPI):
        gemini.conversation_id = ""
        gemini.response_id = ""
        gemini.choice_id = ""

    def _ask_gemini(self, user_prompt: str, gemini: GeminiAPI):
        response = gemini.question(user_prompt)
        self._delay_print(f"{Colors.DARKB}Gemini{Colors.END} : {response}")

    def _get_gemini_instance(self, args_1psid: str, args_1psidts: str) -> GeminiAPI:
        cookies = GeminiCookies.get_configuration(args_1psid, args_1psidts)
        if cookies.get("Secure-1PSID") and cookies.get("Secure-1PSIDTS"):
            return GeminiAPI(cookies=cookies, proxy=self.proxy)
        return None

    def _parse_arguments(self) -> tuple:
        parser = ArgumentParser()
        parser.add_argument("-s", "--session", type=str, help="__Secure-1PSID cookie")
        parser.add_argument(
            "-st", "--session_ts", type=str, help="__Secure-1PSIDTS cookie"
        )
        args = parser.parse_args()
        return args.session, args.session_ts

    def _start_chat(self, gemini: GeminiAPI):
        while True:
            user_prompt = self._get_query(f"\n{Colors.GREEN}You{Colors.END} : ")
            if not self._handle_user_prompt(user_prompt, gemini):
                break

    def _result(self):
        SysOS.clear_console()
        self._instruction()
        config_file_path = Path(GeminiCookies.CONFIG_FILE)

        if config_file_path.exists():
            self._delay_print("✅ Configuration file found!\n")

        args_1psid, args_1psidts = self._parse_arguments()
        gemini = self._get_gemini_instance(args_1psid, args_1psidts)
        self._start_chat(gemini)


if __name__ == "__main__":
    """
    If you want to use a proxy,
    Please update your PROXY in the environment variable or in the .env file.
    Otherwise, leave it as it is; it will be set to None.
    """
    StartGemini(delay=0.002, proxy=getenv("PROXY"))
