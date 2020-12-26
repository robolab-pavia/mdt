# mdt

MarkDown in Terminal - Renders a markdown page in the terminal

## Welcome to MarkDown in Terminal!

Hi! I'm your first Markdown file that you can open with `mdt`. If you want to learn about `mdt`, you can clone this repository and open me from the terminal with

```
mdt README.md
```

If you want to play with Markdown, you can edit me. Once you have finished with me, you can run me in your terminal.

## Project

This project is a Markdown file reader for your terminal.

`mdt` is built with Python, and uses the following libraries:

* [Mistletoe](https://github.com/miyuchina/mistletoe) to parse Markdown files.
* [Python Prompt Toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for the interactive mode.
* [Click](https://click.palletsprojects.com/en/7.x/) to handle commmand line parameters.
* [ansiwrap](https://pypi.org/project/ansiwrap/) to perform the word wrapping.

## Features

`mdt` has the following features:

* Interactive mode with dynamic adaptation to the terminal width.
* You can choose your favourite among some available themes.
* You can edit a them of add your own custom theme. Themes are defined with a simple JSON "CSS-like" format.
* Intelligent word wrapping.

In interactive mode you can:

* Open web links in the default *browser* (requires a graphic sessions to work).
* Follow links to local files forward and backward, allowing a convenient exploration of "wiki-style" files.

## Installation

Clone the repository.

If you have administration permissions, run:

```
python3 setup.py install
```

Otherwise you can install `mdt` for your own user only with:

```
python3 setup.py install --user
```

## Options

The following options are available:

```
$ mdt --help
Usage: mdt [OPTIONS] [MDFILE]

Options:
  --gallery          Print a demo gallery of the available themes.
  -i                 Interactive mode.
  -l                 List all the default themes.
  --col INTEGER      Set the text width in number of columns.
  --rmargin INTEGER  Set the right right margin.
  --theme INTEGER    Choose a default theme by ID.
  --theme-file TEXT  Choose a theme file.
  --help             Show this message and exit.
```
