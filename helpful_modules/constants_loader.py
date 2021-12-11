import dotenv, os


class BotConstants:
    "Bot constants"

    def __init__(self, env_path):
        dotenv.load_dotenv(env_path)
        self.MYSQL_USERNAME = os.environ.get("mysql_username")
        self.MYSQL_PASSWORD = os.environ.get("mysql_password")
        self.MYSQL_DB_IP = os.environ.get("mysql_db_ip")
        self.MYSQL_DB_NAME = os.environ.get("mysql_db_name")
        self.DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
        self.USE_SQLITE = os.environ.get("use_sqlite") == "True"
        self.SQLITE_DB_PATH = os.environ.get("sqlite_database_path")
        self.GITHUB_REPO_LINK = os.environ.get("github_repo_link")
