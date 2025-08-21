"""
Setup script for the portfolio package.
Run 'pip install -e .' to install in development mode.
"""
from setuptools import setup, find_packages

setup(
    name="portfolio",
    version="0.1.0",
    packages=find_packages(include=['portfolio*']),
    install_requires=[
        'fastapi>=0.68.0',
        'uvicorn>=0.15.0',
        'websockets>=10.0',
        'pydantic>=1.8.0',
        'python-jose[cryptography]>=3.3.0',
        'passlib[bcrypt]>=1.7.4',
        'python-multipart>=0.0.5',
        'sqlalchemy>=1.4.0',
        'psycopg2-binary>=2.9.0',
        'python-dotenv>=0.19.0',
        'email-validator>=1.1.3',
        'pytest>=6.0.0',
        'pytest-asyncio>=0.15.0',
    ],
    python_requires='>=3.7',
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.json', '*.yaml'],
    },
)
