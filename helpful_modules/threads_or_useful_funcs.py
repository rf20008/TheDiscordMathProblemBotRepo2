from . import save_files
from time import sleep
from .the_documentation_file_loader import DocumentationFileLoader

def the_daemon_file_saver(bot):
    "Auto-save files!"
    global guildMathProblems, trusted_users, vote_threshold

    FileSaverObj = save_files.FileSaver(
        name="The Daemon File Saver", enabled=True, printSuccessMessagesByDefault=True
    )
    FileSaverDict = FileSaverObj.load_files(bot.cache, True)
    (guildMathProblems, bot.trusted_users, vote_threshold) = (
        FileSaverDict["guildMathProblems"],
        FileSaverDict["trusted_users"],
        FileSaverDict["vote_threshold"],
    )

    while True:
        sleep(45)
        FileSaverObj.save_files(
            bot.cache,
            False,
            guildMathProblems,
            vote_threshold,
            bot.trusted_users,
        )


def generate_new_id():
    "Generate a random number from 0 to 10^14"
    return random.randint(0, 10 ** 14)

def get_git_revision_hash() -> str:
    "A method that gets the git revision hash. Credit to https://stackoverflow.com/a/21901260 for the code :-)"
    return (
        subprocess.check_output(["git", "rev-parse", "HEAD"])
        .decode("ascii")
        .strip()[:7]
    )  # [7:] is here because of the commit hash, the rest of this function is from stack overflow

def loading_documentation_thread():
    "This thread reloads the documentation."
    d = DocumentationFileLoader()
    d.load_documentation_into_readable_files()
    del d