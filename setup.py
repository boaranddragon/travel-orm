from setuptools import setup, find_packages

setup(
    name="travel_orm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "boto3>=1.26.0",
    ],
    description="ORM library for Travel Itinerary application",
    author="Travel Itinerary Team",
    author_email="example@example.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
)
