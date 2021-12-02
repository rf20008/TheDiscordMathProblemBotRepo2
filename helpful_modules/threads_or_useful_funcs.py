from . import save_files
from time import sleep
import subprocess, random
from .the_documentation_file_loader import DocumentationFileLoader


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
