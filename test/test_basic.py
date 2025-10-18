import pytest
from yaso_paste import paste_to_yaso, YasoPasteError

@pytest.mark.asyncio
async def test_text_paste():
    url = await paste_to_yaso("Hello World!", "txt")
    assert url.startswith("https://yaso.su/raw/")

@pytest.mark.asyncio
async def test_file_paste(tmp_path):
    file = tmp_path / "example.txt"
    file.write_text("Hello File!")
    url = await paste_to_yaso(file)
    assert url.startswith("https://yaso.su/raw/")
