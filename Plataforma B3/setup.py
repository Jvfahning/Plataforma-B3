from setuptools import setup, find_packages

setup(
    name="plataforma_b3",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.32.0",
        "sqlalchemy==2.0.25",
        "aiosqlite==0.19.0",
        "aiohttp==3.9.1",
        "python-dotenv==1.0.0",
        "pydantic==2.5.2",
        "pydantic-settings==2.1.0",
    ],
) 