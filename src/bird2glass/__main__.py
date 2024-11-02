"""Main entry point."""

##############################################################################
# Python imports.
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Iterable

##############################################################################
# Local imports.
from .tweet import User, load_javascript, Tweet


##############################################################################
def get_args() -> Namespace:
    """Get the command line arguments.

    Returns:
        The command line arguments.
    """
    parser = ArgumentParser(
        prog="bird2glass",
        description="A tool to convert a Twitter export file into an Obsidian Vault",
    )

    parser.add_argument(
        "tweets",
        type=Path,
        help="The location of the tweets.js file",
    )
    parser.add_argument(
        "vault",
        type=Path,
        help="The directory where the vault files will be created",
    )

    return parser.parse_args()


##############################################################################
def load(tweets: Path) -> Iterable[Tweet]:
    """Load Tweets from the given file.

    Args:
        tweets: The JavaScript file that holds the main Tweet data.

    Yields:
        Tweet objects.
    """
    tweeter = User.from_account(tweets)
    for tweet in load_javascript(tweets):
        yield Tweet(tweet, tweeter)


##############################################################################
def main() -> None:
    """Main entry point."""

    arguments = get_args()

    if not (arguments.tweets.exists() and arguments.tweets.is_file()):
        print("Tweets must be a file and must exist.")
        exit(1)

    if not arguments.vault.is_dir():
        print("The vault must be an existing directory.")
        exit(1)

    for tweet in load(arguments.tweets):
        (arguments.vault / tweet.markdown_directory).mkdir(parents=True, exist_ok=True)
        (arguments.vault / tweet.markdown_file).write_text(tweet.markdown)


##############################################################################
if __name__ == "__main__":
    main()

### __main__.py ends here
