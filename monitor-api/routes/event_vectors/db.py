from dotenv import load_dotenv
from pathlib import Path  # python3 only
import mysql.connector
import os

env_path = os.path.abspath(__file__ + '/../../../.env')
env_path = Path(env_path)
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_DATABSE = os.getenv("DB_DATABASE")
DB_PASSWORD = os.getenv("DB_PASSWORD")

db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USERNAME,
        database=DB_DATABSE,
        password=DB_PASSWORD,
        auth_plugin='mysql_native_password',
    )