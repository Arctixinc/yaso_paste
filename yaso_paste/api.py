import aiohttp
import asyncio
import random
import string
import os
from typing import Union, Tuple

__all__ = ["paste_to_yaso", "YasoPasteError"]

_RETRIES = 3
_TIMEOUT = 10
_BACKOFF = 1.5


class YasoPasteError(Exception):
    """Custom exception for Yaso Paste failures."""


async def _random_string(length: int = 32) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


async def paste_to_yaso(content_or_path: Union[str, os.PathLike], file_extension: str = "txt") -> Tuple[str, str]:
    """
    Paste text content or file to yaso.su and return both the normal and raw URLs.

    Args:
        content_or_path (str or Path): Raw text or path to a file.
        file_extension (str): Optional file extension/language hint (default 'txt').

    Returns:
        Tuple[str, str]: (normal_url, raw_url)

    Raises:
        YasoPasteError: If the paste fails.
    """
    # Read content if a file path is provided
    if os.path.isfile(content_or_path):
        try:
            with open(content_or_path, "r", encoding="utf-8") as f:
                content = f.read()
            _, ext = os.path.splitext(content_or_path)
            if ext:
                file_extension = ext.lstrip(".")
        except Exception as e:
            raise YasoPasteError(f"Failed to read file: {e}")
    else:
        content = str(content_or_path)

    url_auth = "https://api.yaso.su/v1/auth/guest"
    url_record = "https://api.yaso.su/v1/records"
    delay = 1.0

    for attempt in range(1, _RETRIES + 1):
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),
                                             timeout=aiohttp.ClientTimeout(total=_TIMEOUT)) as session:
                # Authenticate as guest
                async with session.post(url_auth) as auth_resp:
                    auth_resp.raise_for_status()

                # Create the paste
                payload = {
                    "captcha": await _random_string(64),
                    "codeLanguage": "auto",
                    "content": content,
                    "extension": file_extension,
                    "expirationTime": 1_000_000
                }

                async with session.post(url_record, json=payload) as paste_resp:
                    paste_resp.raise_for_status()
                    result = await paste_resp.json()
                    paste_id = result.get("url")
                    if not paste_id:
                        raise YasoPasteError(f"Failed to get paste URL: {result}")

                    normal_url = f"https://yaso.su/{paste_id}"
                    raw_url = f"https://yaso.su/raw/{paste_id}"
                    return normal_url, raw_url

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == _RETRIES:
                raise YasoPasteError(f"Network error after {attempt} attempts: {e}")
            await asyncio.sleep(delay)
            delay *= _BACKOFF
        except Exception as e:
            raise YasoPasteError(f"Unexpected error: {e}")
