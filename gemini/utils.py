import os
import sys
from re import sub

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer


class Colors:
    GREEN = "\033[38;5;121m"
    DARKB = "\033[38;5;20m"
    LPURPLE = "\033[38;5;141m"
    END = "\033[0m"


class SysOS:
    @staticmethod
    def clear_console():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def exit_program():
        sys.exit()


class Formatter:
    CODE_INDENTIFIER = "```"
    CODE_INDENT = "        "
    DASH = r"`(.*?)`"

    @classmethod
    def _code_block(cls, text: str) -> str:
        return sub(cls.DASH, r"\g<1>", text)

    @classmethod
    def _highlight_code(cls, text: str) -> str:
        code = highlight(
            text, PythonLexer(), Terminal256Formatter(style="fruity")
        ).strip()
        highlighted_lines = [
            cls.CODE_INDENT + line.replace("python", "") for line in code.splitlines()
        ]
        return "\n".join(highlighted_lines)

    @classmethod
    def final_text(cls, response: str) -> str:
        sections = response.split(cls.CODE_INDENTIFIER)
        return "".join(
            (
                cls._code_block(f"{Colors.LPURPLE}{text}{Colors.END}")
                if idx % 2 == 0
                else cls._highlight_code(text)
            )
            for idx, text in enumerate(sections)
        )
