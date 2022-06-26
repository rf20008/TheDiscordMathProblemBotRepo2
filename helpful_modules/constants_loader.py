import os

import dotenv


class BotConstants:
    """Bot constants"""

    def __init__(self, env_path):
        dotenv.load_dotenv(env_path)
        self.MYSQL_USERNAME = os.environ.get("mysql_username", None)
        self.MYSQL_PASSWORD = os.environ.get("mysql_password", None)
        self.MYSQL_DB_IP = os.environ.get("mysql_db_ip", None)
        self.MYSQL_DB_NAME = os.environ.get("mysql_db_name", None)
        self.DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
        self.USE_SQLITE = os.environ.get("use_sqlite", "true") == "True"
        self.SQLITE_DB_PATH = os.environ.get("sqlite_database_path")
        self.SOURCE_CODE_LINK = os.environ.get(
            "source_code_link",
            "https://github.com/rf20008/TheDiscordMathProblemBotRepo",
        )
        self.BOT_RESTART_CHANNEL = os.environ.get("bot_restart_channel")
        self.SUGGESTIONS_AND_FEEDBACK_CHANNEL_ID = 883908866541256805
        self.SUPPORT_SERVER_ID = 873741593159540747