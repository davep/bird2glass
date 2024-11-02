"""Provides a class for holding data about a tweet."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
from dataclasses import dataclass, field
from datetime import datetime
from json import loads
from pathlib import Path
from typing import Any, cast

##############################################################################
# Date utility imports.
from dateutil.parser import parse


##############################################################################
def load_javascript(javascript: Path) -> list[dict[str, Any]]:
    """Turn Twitter's JavaScript dat ainto JSON.

    Args:
        javascript: The JavaScript source to convert.
        data_type: The type of the data to convert.

    Returns:
        The data as JSON.
    """
    return cast(
        list[dict[str, Any]],
        loads(
            javascript.read_text().removeprefix(
                f"window.YTD.{javascript.stem}.part0 = "
            )
        ),
    )


##############################################################################
@dataclass
class User:
    """Class that holds data of a user."""

    identity: str = ""
    """The user's ID."""
    handle: str = ""
    """The user's twitter handle."""
    name: str = ""
    """The user's name."""

    def __init__(self, user: dict[str, Any]) -> None:
        self.identity = user["id_str"]
        self.handle = user["screen_name"]
        self.name = user["name"]

    @classmethod
    def from_account(cls, tweets: Path) -> User:
        account_data = load_javascript(tweets.parent / "account.js")[0]
        return cls(
            {
                "id_str": account_data["account"]["accountId"],
                "screen_name": account_data["account"]["username"],
                "name": account_data["account"]["accountDisplayName"],
            }
        )


##############################################################################
@dataclass
class Tweet:
    """Class that holds data for a Tweet."""

    identity: str = ""
    """The ID of the Tweet."""
    full_text: str = ""
    """The full text of the Tweet."""
    mentions: list[User] = field(default_factory=list)
    """The users mentioned in the Tweet."""
    in_reply_to: User | None = None
    """The user the Tweet was in reply to, if any."""
    favourite_count: int = 0
    """The number of favourites for this Tweet."""
    retweet_count: int = 0
    """The number of retweets for this Tweet."""
    tweeted: datetime = field(default_factory=lambda: datetime(0, 0, 0))
    """The time the Tweet was sent."""

    def __init__(self, tweet: dict[str, Any], tweeter: User) -> None:
        data = tweet["tweet"]
        self.identity = data["id_str"]
        self.full_text = data["full_text"]
        self.mentions = [User(user) for user in data["entities"]["user_mentions"]]
        self.favourite_count = int(data["favorited"])
        self.retweet_count = int(data["retweet_count"])
        self.tweeted = parse(data["created_at"])
        if "in_reply_to_user_id" in data:
            self.in_reply_to = next(
                (
                    user
                    for user in self.mentions
                    if user.identity == data["in_reply_to_user_id"]
                ),
                tweeter,
            )

    @property
    def markdown_directory(self) -> Path:
        """The directory for the Markdown file associated with this tweet."""
        return Path(self.tweeted.strftime("%Y/%m/%d/"))

    @property
    def markdown_file(self) -> Path:
        """The name of the Markdown file for this Tweet."""
        return self.markdown_directory / Path(self.identity).with_suffix(".md")


### tweet.py ends here
