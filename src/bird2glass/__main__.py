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

    for tweet in load(arguments.tweets):
        print(tweet.markdown_file)


##############################################################################
if __name__ == "__main__":
    main()

### __main__.py ends here
