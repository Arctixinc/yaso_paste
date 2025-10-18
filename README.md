# Async Python library to paste **text or files** to [yaso.su](https://yaso.su).

## Installation

```bash
pip install yaso-paste
````

## Usage

### Paste raw text

```python
import asyncio
from yaso_paste import paste_to_yaso

async def main():
    url = await paste_to_yaso("print('Hello World!')", "py")
    print(url)

asyncio.run(main())
```

### Paste file contents

```python
import asyncio
from yaso_paste import paste_to_yaso

async def main():
    url = await paste_to_yaso("example.py")  # will read file contents
    print(url)

asyncio.run(main())
```

## Features

* Paste raw text or file contents.
* Automatically detects file extension if not provided.
* Async, with retries and timeout handling.
* Simple 1-function API: `paste_to_yaso()`.
