import json
import os
import sys
from random import randint
from re import search, sub
from textwrap import dedent
from time import sleep
from typing import Dict

from dotenv import load_dotenv
from halo import Halo
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer
from requests import Session
from spinners import Spinners


class Colors:
    GREEN = '\033[38;5;121m'
    DARKB = '\033[38;5;20m'
    LPURPLE = '\033[38;5;141m'
    END = '\033[0m'


class Utils:
    @staticmethod
    def clear_console():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def exit_program():
        sys.exit()


class Formatter:
    CODE_INDENTIFIER = '```'
    CODE_INDENT = '        '
    DASH = r'`(.*?)`'

    @classmethod
    def code_block(
        cls,
        text: str
        ) -> str:

        return sub(cls.DASH, r'\g<1>', text)

    @classmethod
    def highlight_code(
        cls,
        text: str
        ) -> str:

        code = highlight(text, PythonLexer(), Terminal256Formatter(style='fruity')).strip()
        highlighted_text = ''
        for line in code.splitlines():
            line = line.replace('python', '')
            highlighted_text += f'{cls.CODE_INDENT}{line}\n'
        return highlighted_text

    @classmethod
    def final_text(
        cls,
        response: str
        ) -> str:

        formatted_text = ''
        for idx, text in enumerate(response.split(cls.CODE_INDENTIFIER)):
            if not idx % 2:
                text = cls.code_block(f'{Colors.LPURPLE}{text}{Colors.END}')
                formatted_text += text
            else:
                formatted_text += cls.highlight_code(text)
        return formatted_text


class BardAPI:
    BASE_URL = 'https://bard.google.com'

    def __init__(
        self,
        session_id: str,
        proxy: str = None
        ):

        self.spinner = Halo(text_color='blue', spinner=Spinners['point'].value, color='magenta')
        self.reqid = randint(100000, 900000)
        self.conversation_id = ''
        self.response_id = ''
        self.choice_id = ''
        self.session = Session()
        self.session.proxies.update({'http': proxy, 'https': proxy}) if proxy else None
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'})
        self.session.cookies.set('__Secure-1PSID', session_id)
        self.snlm0e = self.get_snlm0e()

    def __del__(self):
        self.session.close()
        print('Session Closed!')

    def get_snlm0e(self) -> str:
        with self.spinner as status:
            status.start('Loading..')
            sleep(1)
            try:
                response = self.session.get(
                    self.BASE_URL,
                    timeout=10
                )
            except Exception as exc:
                status.fail(f'Requests encountered an error: {str(exc)}')
                Utils.exit_program()
            else:
                snlm0e = search(r'SNlM0e":"(.*?)"', response.text)
                if snlm0e is None:
                    status.warn('Fail to get BardAI!')
                    Utils.exit_program()
                else:
                    snlm0e = snlm0e[1]
                    status.succeed(f'Welcome to BardAI!')
                    return snlm0e

    def question(
        self,
        message: str
        ) -> str:

        params = {
            'bl': 'boq_assistant-bard-web-server_20230514.20_p0',
            '_reqid': str(self.reqid),
            'rt': 'c',
        }

        message_body = [
            [message],
            None,
            [self.conversation_id, self.response_id, self.choice_id],
        ]

        data = {
            'f.req': json.dumps([None, json.dumps(message_body)]),
            'at': self.snlm0e,
        }

        with self.spinner as status:
            status.start('Please wait! Bard is thinking ..')
            try:
                response = self.session.post(
                    f'{self.BASE_URL}/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate',
                    params=params,
                    data=data,
                    timeout=120,
                )
            except Exception as exc:
                status.fail(f'Requests encountered an error: {str(exc)}')
                Utils.exit_program()

            else:
                chat_data = json.loads(response.content.splitlines()[3])[0][2]
                if not chat_data:
                    status.warn(f'Chat data encountered an error: {response.content}.')
                    Utils.exit_program()

                json_chat_data = json.loads(chat_data)
                results = {
                    'content': json_chat_data[0][0],
                    'conversation_id': json_chat_data[1][0],
                    'response_id': json_chat_data[1][1],
                    'factualityQueries': json_chat_data[3],
                    'textQuery': json_chat_data[2][0] if json_chat_data[2] is not None else '',
                    'choices': [{'id': i[0], 'content': i[1]} for i in json_chat_data[4]],
                }
                self.conversation_id = results['conversation_id']
                self.response_id = results['response_id']
                self.choice_id = results['choices'][0]['id']
                self.reqid += 100000
                status.succeed('Solution Found!')
                return Formatter.final_text(results['content'])


class BardCookies:
    CONFIG_FILE = 'bard_cookies.json'
    MISSING_CONFIG = dedent("""
    ⚠️  Could not find BARD_COOKIES in environment variables or configuration.
    ⚠️  Please choose one of the following options:
        [1] Manually enter BARD_COOKIES
        [2] Exit
    """)

    @staticmethod
    def user_choice() -> Dict[str, str]:
        while True:
            user_choice = input('Enter your choice: ')
            if user_choice == '2':
                Utils.exit_program()
            elif user_choice == '1':
                return {'BARD_COOKIES': input('Enter __Secure-1PSID cookie: ')}
            else:
                print('Wrong input! Please check your value!')

    @classmethod
    def save_config(cls, config: Dict[str, str]):
        with open(cls.CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
        print(f'\n"{cls.CONFIG_FILE}" file has been created successfully.\n')

    @classmethod
    def load_config(cls) -> Dict[str, str]:
        try:
            with open(cls.CONFIG_FILE, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return {}

    @classmethod
    def prompt_user_choice(cls) -> Dict[str, str]:
        print(cls.MISSING_CONFIG)
        return cls.user_choice()

    @classmethod
    def set_bard_cookies(cls, bard_cookies: str):
        cls.save_config({'BARD_COOKIES': bard_cookies})

    @classmethod
    def get_bard_cookies(cls, session: str) -> str:
        load_dotenv()
        bard_cookies = os.getenv('BARD_COOKIES')

        if not bard_cookies:
            if session:
                bard_cookies = session
            else:
                config = cls.prompt_user_choice()
                bard_cookies = config['BARD_COOKIES']
            cls.set_bard_cookies(bard_cookies)

        return bard_cookies

    @classmethod
    def get_configuration(cls, session: str) -> Dict[str, str]:
        config = cls.load_config()
        bard_cookies = config.get('BARD_COOKIES')

        if not bard_cookies:
            bard_cookies = cls.get_bard_cookies(session)

        config['BARD_COOKIES'] = bard_cookies
        return config
