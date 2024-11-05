"""Provides a class for holding data about a tweet."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
from dataclasses import dataclass, field
from datetime import datetime
from json import loads
from pathlib import Path
from re import compile
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
        """Initialise the User.

        Args:
            args: The user data.
        """
        self.identity = user["id_str"]
        self.handle = user["screen_name"]
        self.name = user["name"]

    @classmethod
    def from_account(cls, tweets: Path) -> User:
        """Create a `User` instance from the account of the archive.

        Args:
            tweets: The path to the file that contains the tweets.

        Returns:
            An instance of `User` for the author of the tweets.
        """
        account_data = load_javascript(tweets.parent / "account.js")[0]
        return cls(
            {
                "id_str": account_data["account"]["accountId"],
                "screen_name": account_data["account"]["username"],
                "name": account_data["account"]["accountDisplayName"],
            }
        )

    @property
    def markdown_directory(self) -> Path:
        """The directory for the user."""
        return Path("accounts/")

    @property
    def markdown_file(self) -> Path:
        """The name of the Markdown file for this user."""
        return (self.markdown_directory / self.handle).with_suffix(".md")

    @property
    def url(self) -> str:
        """The URL for the user."""
        return f"https://x.com/{self.handle}"

    @property
    def markdown(self) -> str:
        """Markdown text for this user."""
        return f'---\naliases:\n  - "@{self.handle}"\n  - "{self.name}"\nname: "{self.name}"\nurl: {self.url}\n---'


##############################################################################
@dataclass
class Tweet:
    """Class that holds data for a Tweet."""

    tweeter: User
    """The `User` data of the tweeter of this tweet."""
    identity: str = ""
    """The ID of the Tweet."""
    full_text: str = ""
    """The full text of the Tweet."""
    mentions: list[User] = field(default_factory=list)
    """The users mentioned in the Tweet."""
    in_reply_to_user: User | None = None
    """The user the Tweet was in reply to, if any."""
    in_reply_to_tweet: str | None = None
    """The tweet this Tweet was in reply to, if it is a reply."""
    favourite_count: int = 0
    """The number of favourites for this Tweet."""
    retweet_count: int = 0
    """The number of retweets for this Tweet."""
    tweeted: datetime = field(default_factory=lambda: datetime(0, 0, 0))
    """The time the Tweet was sent."""
    media: list[str] = field(default_factory=list)
    """The list of media files associated with this Tweet."""
    twitpics: list[str] = field(default_factory=list)
    """List of URLs of images hosted on TwitPic"""

    _TWITPIC = compile(r"https?://twitpic\.com/\w+")
    """Regular expression for finding images posted on TwitPic."""

    def __init__(self, tweet: dict[str, Any], tweeter: User) -> None:
        """Initialise the Tweet object.

        Args:
            tweet: The Tweet data.
            tweeter: The `User` details of the author of the tweets.
        """
        data = tweet["tweet"]
        self.tweeter = tweeter
        self.identity = data["id_str"]
        self.full_text = data["full_text"]
        self.mentions = [User(user) for user in data["entities"]["user_mentions"]]
        self.favourite_count = int(data["favorited"])
        self.retweet_count = int(data["retweet_count"])
        self.tweeted = parse(data["created_at"])
        self.media = [
            (
                f"{self.identity}-{Path(media['media_url']).stem}.mp4"
                if media["type"] in ("video", "animated_gif")
                else f"{self.identity}-{Path(media['media_url']).name}"
            )
            for media in data.get("extended_entities", {}).get("media", [])
            or data.get("entities", {}).get("media", [])
        ]
        if "in_reply_to_user_id" in data:
            self.in_reply_to_user = next(
                (
                    user
                    for user in self.mentions
                    if user.identity == data["in_reply_to_user_id"]
                ),
                tweeter,
            )
            if "in_reply_to_status_id" in data:
                self.in_reply_to_tweet = f"{self.in_reply_to_user.url}/status/{data['in_reply_to_status_id']}"
        self.twitpics = self._TWITPIC.findall(self.full_text)

    @property
    def markdown_directory(self) -> Path:
        """The directory for the Markdown file associated with this tweet."""
        return Path(self.tweeted.strftime("%Y/%m/%d/"))

    @property
    def markdown_attachment_directory(self) -> Path:
        """The directory where attachments for this tweet will live in Markdown."""
        return self.markdown_directory / "attachments"

    @property
    def markdown_file(self) -> Path:
        """The name of the Markdown file for this Tweet."""
        return self.markdown_directory / Path(self.identity).with_suffix(".md")

    @property
    def url(self) -> str:
        """The URL of this tweet."""
        return f"{self.tweeter.url}/status/{self.identity}"

    @property
    def _front_matter(self) -> str:
        """The front matter for the Markdown version of the tweet."""
        return "\n".join(
            matter
            for matter in (
                f"tweeted-at: {self.tweeted}",
                f"favourite-count: {self.favourite_count}",
                f"retweet-count: {self.retweet_count}",
                f"is-reply: {'no' if self.in_reply_to_user is None else 'yes'}",
                f"replying-to: {self.in_reply_to_tweet}"
                if self.in_reply_to_tweet is not None
                else "",
                f"url: {self.url}",
                f"attachment-count: {len(self.media) + len(self.twitpics)}",
            )
            if matter
        )

    _HANDLE = compile(r"@([A-Za-z0-9_]{1,15})")
    """Regular expression for finding a Twitter handle in some text."""

    @property
    def _markedup_full_text(self) -> str:
        """The full text of the tweet, marked up for Markdown."""
        return self._HANDLE.sub(r"[[\1|@\1]]", self.full_text)

    @property
    def _markdown_media(self) -> str:
        """The Markdown for all the media attached to this Tweet."""
        media = [f"![[{media}]]" for media in self.media] + [
            f'<iframe src="{twicpic}" style="overflow: auto; resize: both; aspect-ratio: 1/1; width: 100%; height: 100%;"></iframe>'
            for twicpic in self.twitpics
        ]
        return f"\n---\n{'\n'.join(media)}" if media else ""

    @property
    def markdown(self) -> str:
        """The Markdown representation of the Tweet."""
        return f"---\n{self._front_matter}\n---\n\n{self._markedup_full_text}\n{self._markdown_media}"


### tweet.py ends here
