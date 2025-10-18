import pytest
from yaso_paste import paste_to_yaso, YasoPasteError

@pytest.mark.asyncio
async def test_text_paste():
    normal_url, raw_url = await paste_to_yaso("Hello World!", "txt")
    assert normal_url.startswith("https://yaso.su/")
    assert raw_url.startswith("https://yaso.su/raw/")

@pytest.mark.asyncio
async def test_file_paste(tmp_path):
    file = tmp_path / "example.txt"
    file.write_text("Hello File!")
    normal_url, raw_url = await paste_to_yaso(file)
    assert normal_url.startswith("https://yaso.su/")
    assert raw_url.startswith("https://yaso.su/raw/")
