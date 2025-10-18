from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yaso-paste",
    version="3.0.0",
    author="Arctix",
    author_email="inc.arctix@gmail.com",
    description="Async Python library to paste text or files to yaso.su",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Arctixinc/yaso_paste",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8,<4.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
