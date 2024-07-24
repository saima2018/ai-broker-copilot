import json
import os
import sys
import time
import warnings
from difflib import SequenceMatcher
from functools import wraps

import regex
import tiktoken
import requests
from commons.cfg_loader import project_cfg



def parse_text(text: str):
    """copy from https://github.com/GaiZhenbiao/ChuanhuChatGPT/"""
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    count = 0
    for i, line in enumerate(lines):
        if "```" in line:
            count += 1
            items = line.split('`')
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = f'<br></code></pre>'
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", "\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                lines[i] = "<br>" + line
    text = "".join(lines)
    return text


def extract_en_chn(text):
    en = ''
    chn = ''
    for char in text:
        if '\u0041' <= char <= '\u005a' or '\u0061' <= char <= '\u007a':  # ASCII 字母
            en += char
        elif '\u4e00' <= char <= '\u9fff':  # 中文范围
            chn += char
    return en, chn


def num_tokens_from_string(string: str, encoding_name: str = "gpt-3.5-turbo", cn_factor: float = 2.17) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = 0
    encoding = tiktoken.encoding_for_model(encoding_name)
    en, chn = extract_en_chn(string)
    num_tokens += len(encoding.encode(en))
    num_tokens += len(encoding.encode(chn)) * cn_factor
    return int(num_tokens)


def get_stream_request_result(
        url: str,
        question: str,
        temperature=0.7,
        top_p=1):
    params = {
        "question": question,
        "temperature": temperature,
        "top_p": top_p,
    }
    resp = requests.post(url, data=json.dumps(params), stream=True)
    # show_content = ""
    for content in resp.iter_content(decode_unicode=True, chunk_size=1):
        # print(content)
        parsed_content = parse_text(content)
        # show_content += parsed_content
        yield parsed_content


def retry(total_tries: int, initial_wait=1, backoff_factor=1.5, logger=None):
    assert total_tries > 0, "total_tries must be an int larger than 0"

    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = total_tries + 1, initial_wait
            while _tries > 1:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    _tries -= 1
                    if _tries == 1:
                        msg = str(
                            f"Function: ({f.__name__}) failed after {total_tries} tries\n"
                        )
                        if logger is not None:
                            logger.error(msg)
                        else:
                            warnings.warn(msg)
                        raise
                    msg = str(
                        f"Function: ({f.__name__}) failed due to {e}\n retrying in {_delay} seconds!"
                    )
                    if logger is not None:
                        logger.warning(msg)
                    else:
                        warnings.warn(msg)
                    time.sleep(_delay)
                    _delay *= backoff_factor

        return func_with_retries

    return retry_decorator




def get_pe_version():
    return project_cfg.version


# 给str前后加入颜色,方便print或log输出
def add_color(s, color='red'):
    if color == 'red':
        return f'\033[31m{s}\033[0m'
    elif color == 'green':
        return f'\033[32m{s}\033[0m'
    elif color == 'yellow':
        return f'\033[33m{s}\033[0m'
    elif color == 'blue':
        return f'\033[34m{s}\033[0m'
    elif color == 'purple':
        return f'\033[35m{s}\033[0m'
    elif color == 'cyan':
        return f'\033[36m{s}\033[0m'
    elif color == 'white':
        return f'\033[37m{s}\033[0m'
    else:
        return s


def remove_emojis(text):
    # Define the regex pattern for emojis
    emoji_pattern = regex.compile("[\U00010000-\U0010FFFF]", flags=regex.UNICODE)
    # Substitute the matched emojis with an empty string
    return emoji_pattern.sub(r'', text)


def normalize_quotes(s):
    # Strip any whitespace that might be around the string
    s = s.strip()

    # Check if the string starts and ends with either single or double quotes
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        # If it is already correctly quoted, remove the leading and trailing quotes and then wrap it with single quotes
        s = s[1:-1]
    elif s.startswith("'") and s.endswith('"'):
        # If it starts with a single quote and ends with a double quote, remove them and wrap with single quotes
        s = s[1:-1]
    elif s.startswith('"') and s.endswith("'"):
        # If it starts with a double quote and ends with a single quote, remove them and wrap with single quotes
        s = s[1:-1]
    else:
        # If there are no quotes, simply wrap the string with single quotes
        s = s
    # print('s', s)
    return s


def find_best_string_match(string_list, target):
    best_match = None
    highest_ratio = 0.0

    for s in string_list:
        matcher = SequenceMatcher(None, target, s)
        ratio = matcher.ratio()
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = s

    return best_match


class LazyCallable:
    def __init__(self, name):
        self.n, self.f = name, None
    def __call__(self, *args, **kwargs):
        if self.f is None:
            modn, funcn = self.n.rsplit('.', 1)
            if modn not in sys.modules:
                __import__(modn)
            module = sys.modules[modn]
            try:
                self.f = getattr(module, funcn)
            except AttributeError:
                raise AttributeError(f'Function {funcn} not found in module {modn}')
        if not callable(self.f):
            raise TypeError(f"The attribute '{self.n}' is not callable.")
        return self.f(*args, **kwargs)

if __name__ == '__main__':
    # normalize_quotes("'abc'")
    import agents.trading