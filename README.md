# bird2glass

## Introduction

This is a simple command line tool that can be used to turn a Twitter
archive into an Obsidian Vault.

> [!NOTE]
> This code was written while working with a Twitter archive created in
> 2022, in the days before Twitter had the new owner. I've since stopped
> using Twitter and have no idea if the form of the archive is the same.

![Graph view of my Tweets](./imgs/bird2glass.png)

## Installing

### pipx

The package can be installed using [`pipx`](https://pypa.github.io/pipx/):

```sh
$ pipx install bird2glass
```

### Homebrew

The package is available via Homebrew. Use the following commands to install:

```sh
$ brew tap davep/homebrew
$ brew install bird2glass
```

## Usage

### Prepare for the conversion

1. Extract your Twitter archive into a directory.
2. Create a directory that will become the vault.

### Do the conversion

```sh
bird2glass tweets-file obsidian-vault
```

where `tweets-file` is the file that contains all of your tweets (this
should be `tweets.js` within the extracted directory) and `obsidian-vault`
is the directory you created that will be the Obsidian Vault.

## Notes and assumptions

This tool was built in part as an experiment in what can be done with
Obsidian, in part for fun, and fully for my own needs. As such there might
be assumptions and design decisions in here that won't match what you need.
Updates to make the code more general are welcome; likewise hacking it to
make it work "just so" for you is encouraged.

Some things to note:

- Everything relating to hashtags is left to Obsidian's understanding of
  hashtags. I don't know if Twitter and Obsidian's "specification" for a
  hashtag are the same, but I'm working on the assumption they are.
- Every single tweet is turned into its own Markdown file. If you tweeted a
  lot, expect a *lot* of files to be created.
- Back in the day, before you could attach media to tweets, I used TwitPic a
  lot. This tool attempts to detect TwicPic images and tries to embed them
  using an `iframe`.

## Getting help

If you need help please feel free to [raise an
issue](https://github.com/davep/bird2glass/issues).

[//]: # (README.md ends here)
