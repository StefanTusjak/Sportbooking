from dotenv import load_dotenv
import os

def load_config(testing=False):
    env_file = ".env.test" if testing else ".env"
    load_dotenv(dotenv_path=env_file)

    return {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }
