# mdt

MarkDown in Terminal - Renders a markdown page in the terminal

## Welcome to MarkDown in Terminal!

Hi! I'm your first Markdown file that you can open with `mdt`. If you want to learn about `mdt`, you can clone this repository and open me from the terminal with

```
mdt README.md
```

If you want to play with Markdown, you can edit me. Once you have finished with me, you can run me in your terminal.

## Project

This project is a markdown file reader from your terminal.

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
