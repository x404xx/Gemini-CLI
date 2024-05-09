import json
from random import randint
from re import search

from requests import Session

from console import Halo

from .utils import Formatter, SysOS


class GeminiAPI:
    BASE_URL = "https://gemini.google.com"

    def __init__(self, cookies: dict, proxy: str = None):
        self.spinner = Halo(text_color="blue", spinner="point", color="magenta")
        self.reqid = randint(100000, 899999)
        self.conversation_id = ""
        self.response_id = ""
        self.choice_id = ""
        self.session = Session()
        self.session.proxies.update({"http": proxy, "https": proxy})
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
        )
        self.session.cookies.set("__Secure-1PSID", cookies["Secure-1PSID"])
        self.session.cookies.set("__Secure-1PSIDTS", cookies["Secure-1PSIDTS"])
        self.snlm0e = self._get_snlm0e()

    def __del__(self):
        self.session.close()
        print("Session Closed!")

    def _make_request(self, method, url, message=None, **kwargs):
        with self.spinner as status:
            status.start("Loading..")
            try:
                response = getattr(self.session, method)(url, **kwargs)
                if message:
                    status.succeed(message)
                return response
            except Exception as exc:
                status.fail(f"Requests encountered an error: {str(exc)}")
                SysOS.exit_program()

    def _get_snlm0e(self) -> str:
        response = self._make_request(
            "get", f"{self.BASE_URL}/app", timeout=10, message="Welcome to GeminiAI!"
        )
        if matches := search(r'SNlM0e":"(.*?)"', response.text):
            return matches[1]

        self.spinner.fail(
            "Fail to get GeminiAI! Please check your cookies or just update with a new cookies."
        )
        SysOS.exit_program()

    def _prepare_data(self, message: str):
        message_body = [
            [message],
            None,
            [self.conversation_id, self.response_id, self.choice_id],
        ]
        return {
            "f.req": json.dumps([None, json.dumps(message_body)]),
            "at": self.snlm0e,
        }

    def question(self, message: str) -> str:
        params = {
            "bl": "boq_assistant-bard-web-server_20240505.09_p1",
            "_reqid": str(self.reqid),
            "rt": "c",
        }
        data = self._prepare_data(message)
        response = self._make_request(
            "post",
            f"{self.BASE_URL}/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate",
            params=params,
            data=data,
            timeout=60,
        )
        chat_data = json.loads(response.content.splitlines()[3])[0][2]
        if not chat_data:
            self.spinner.warn(f"Gemini encountered an error: {response.content}.")
            SysOS.exit_program()
        json_chat_data = json.loads(chat_data)
        results = {
            "content": json_chat_data[4][0][1][0],
            "conversation_id": json_chat_data[1][0],
            "response_id": json_chat_data[1][1],
            "factualityQueries": json_chat_data[3],
            "textQuery": (
                json_chat_data[2][0] if json_chat_data[2] is not None else ""
            ),
            "choices": [{"id": i[0], "content": i[1]} for i in json_chat_data[4]],
        }
        self.conversation_id = results["conversation_id"]
        self.response_id = results["response_id"]
        self.choice_id = results["choices"][0]["id"]
        self.reqid += 100000
        self.spinner.succeed("Solution Found!")
        return Formatter.final_text(results["content"])
