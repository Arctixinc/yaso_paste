import pytest
import asyncio
from pathlib import Path
from unittest.mock import patch, AsyncMock
from yaso_paste import paste_to_yaso, YasoPasteError

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
    # Point to a non-existent file
    file = tmp_path / "nonexistent.txt"
    with pytest.raises(YasoPasteError) as excinfo:
        await paste_to_yaso(file)
    assert "Failed to read file" in str(excinfo.value)

@pytest.mark.asyncio
async def test_network_failure_retry():
    # Patch aiohttp.ClientSession to simulate network error
    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        # Simulate raising a ClientError for every call
        mock_post.side_effect = Exception("Simulated network error")

        with pytest.raises(YasoPasteError) as excinfo:
            await paste_to_yaso("Hello World!")
        assert "Unexpected error" in str(excinfo.value)
