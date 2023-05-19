from argparse import ArgumentParser
from pathlib import Path
from sys import stdout
from textwrap import dedent
from time import sleep

from classes import BardAPI, BardCookies, Colors, Utils


class StartBard:
    def __init__(
        self, delay: float = 0.003
        ):

        self.delay = delay
        self.result()

    def delay_print(
        self, words: str
        ):

        for word in words:
            stdout.write(word)
            stdout.flush()
            sleep(self.delay)
        stdout.write('\n')

    def get_query(
        self,
        prompt: str
        ) -> str:

        print(prompt, end='')
        return '\n'.join(iter(input, ''))

    def handle_user_prompt(
        self, user_prompt: str, bard: BardAPI
        ) -> bool:

        if user_prompt == '!exit':
            return False
        elif user_prompt == '!clear':
            Utils.clear_console()
        elif user_prompt == '!reset':
            self.reset_bard(bard)
            Utils.clear_console()
        else:
            self.ask_bard(user_prompt, bard)
        return True

    def reset_bard(
        self, bard: BardAPI
        ):

        bard.conversation_id = ''
        bard.response_id = ''
        bard.choice_id = ''

    def ask_bard(
        self, user_prompt: str, bard: BardAPI
        ):

        response = bard.question(user_prompt)
        self.delay_print(f'{Colors.DARKB}Bard{Colors.END} : {response}')

    def get_bard_instance(
        self, session: str
        ) -> BardAPI:

        config = BardCookies.get_configuration(session)
        if config.get('BARD_COOKIES'):
            return BardAPI(session_id=config['BARD_COOKIES'])
        return None

    def parse_arguments(self) -> str:
        parser = ArgumentParser()
        parser.add_argument('--session', nargs='?', help='__Secure-1PSID cookie')
        args = parser.parse_args()
        return args.session

    def start_chat(
        self,
        bard: BardAPI
        ):

        while True:
            user_prompt = self.get_query(f'\n{Colors.GREEN}You{Colors.END} : ')
            if not self.handle_user_prompt(user_prompt, bard):
                break

    def result(self):
        Utils.clear_console()

        print(dedent("""
            CLI tool for interacting with Google's Bard chatbot (https://bard.google.com)
               [!] PLEASE DOUBLE 'enter' TO SEND A MESSAGE.
                  - Type !clear to clear the console.
                  - Type !reset to reset the conversation.
                  - Type !exit to exit the program.
        """))

        config_file_path = Path(BardCookies.CONFIG_FILE)

        if config_file_path.exists():
            print('Found configuration file!')

        session = self.parse_arguments()
        bard = self.get_bard_instance(session)
        self.start_chat(bard)


if __name__ == '__main__':
    StartBard(delay=0.002)

