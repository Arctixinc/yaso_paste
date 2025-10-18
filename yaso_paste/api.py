import aiohttp
import asyncio
import random
import string
import os
from typing import Union

__all__ = ["paste_to_yaso", "YasoPasteError"]

_RETRIES = 3
_TIMEOUT = 10
_BACKOFF = 1.5


class YasoPasteError(Exception):
    """Custom exception for Yaso Paste failures."""


async def _generate_random_string(length: int = 32) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


async def paste_to_yaso(content_or_path: Union[str, os.PathLike], file_extension: str = "txt") -> str:
    """
    Paste text content or file to yaso.su and return the raw URL.

    Args:
        content_or_path (str or Path): Raw text or path to a file.
        file_extension (str): Optional file extension/language hint (default 'txt').

    Returns:
        str: URL of the paste.

    Raises:
        YasoPasteError: If the paste fails (network error, invalid file, or API failure).
    """
    # Read content from file if path is provided
    if os.path.isfile(content_or_path):
        try:
            with open(content_or_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise YasoPasteError(f"Failed to read file: {e}")

        if file_extension == "txt":
            _, ext = os.path.splitext(content_or_path)
            if ext:
                file_extension = ext.lstrip(".")
    else:
        content = str(content_or_path)

    url_auth = "https://api.yaso.su/v1/auth/guest"
    url_record = "https://api.yaso.su/v1/records"
    delay = 1.0

    for attempt in range(1, _RETRIES + 1):
        try:
            # Use a fresh session per call to avoid "event loop closed" errors
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),
                                             timeout=aiohttp.ClientTimeout(total=_TIMEOUT)) as session:

                # Authenticate as guest
                async with session.post(url_auth) as auth_resp:
                    auth_resp.raise_for_status()

                # Create the paste
                payload = {
                    "captcha": await _generate_random_string(64),
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
                    return f"https://yaso.su/raw/{paste_id}"

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == _RETRIES:
                raise YasoPasteError(f"Network error after {attempt} attempts: {e}")
            await asyncio.sleep(delay)
            delay *= _BACKOFF
        except Exception as e:
            raise YasoPasteError(f"Unexpected error: {e}")
