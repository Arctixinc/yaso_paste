import pytest
from pathlib import Path
from unittest.mock import patch
from yaso_paste import paste_to_yaso, YasoPasteError
import asyncio

# Helper for mocking async context manager
class AsyncContextManager:
    def __init__(self, return_value=None, raise_exc=None):
        self.return_value = return_value
        self.raise_exc = raise_exc

    async def __aenter__(self):
        if self.raise_exc:
            raise self.raise_exc
        return self.return_value

    async def __aexit__(self, exc_type, exc, tb):
        return False

@pytest.mark.asyncio
async def test_text_paste():
    raw_url, normal_url = await paste_to_yaso("Hello World!", "txt")
    assert raw_url.startswith("https://yaso.su/raw/")
    assert normal_url.startswith("https://yaso.su/")

@pytest.mark.asyncio
async def test_file_paste(tmp_path):
    file = tmp_path / "example.txt"
    file.write_text("Hello File!")
    raw_url, normal_url = await paste_to_yaso(file)
    assert raw_url.startswith("https://yaso.su/raw/")
    assert normal_url.startswith("https://yaso.su/")

@pytest.mark.asyncio
async def test_invalid_file(tmp_path):
    # Non-existent file should raise error
    file = tmp_path / "nonexistent.txt"
    with pytest.raises(YasoPasteError) as excinfo:
        await paste_to_yaso(file)
    assert "File does not exist" in str(excinfo.value)

@pytest.mark.asyncio
async def test_network_failure_retry():
    # Patch aiohttp.ClientSession.post to always raise an exception
    with patch("aiohttp.ClientSession.post", return_value=AsyncContextManager(raise_exc=Exception("Simulated network error"))):
        with pytest.raises(YasoPasteError) as excinfo:
            await paste_to_yaso("Hello World!")
        assert "Unexpected error" in str(excinfo.value)
