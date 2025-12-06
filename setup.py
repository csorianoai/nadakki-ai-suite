from setuptools import setup, find_packages

setup(
    name="nadakki-ai-suite",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.5.0",
        "python-multipart==0.0.6",
        "numpy==2.0.0",
        "pandas==2.2.3",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
    ],
)