# mdt

MarkDown in Terminal - Renders a markdown page in the terminal

## Welcome to MarkDown in the Terminal!

Hi! I am your first Markdown file that you can open with `mdt`.
If you want to learn about `mdt`, you can clone this repository and open me from the terminal with

```
mdt show README.md
```

If you want to play with Markdown, you can edit me. Once you have finished with me, you can run me in your terminal.

## Installation

Clone the repository.

If you have administration permissions, run:

```
pip install mdt-viewer
```

## Features

`mdt` has the following features:

* Interactive mode with dynamic adaptation to the terminal width.
* You can choose your favourite among some available themes.
* You can edit a them of add your own custom theme. Themes are defined with a simple JSON "CSS-like" format.
* Intelligent word wrapping.

In interactive mode you can:

* Open web links in the default *browser* (requires a graphic session to work).
* Follow links to local files forward and backward, allowing a convenient exploration of "wiki-style" files.

## Project

`mdt` is built with Python, and uses the following libraries:

* [Mistletoe](https://github.com/miyuchina/mistletoe) to parse Markdown files.
* [Python Prompt Toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for the interactive mode.
* [Click](https://click.palletsprojects.com/en/7.x/) to handle commmand line parameters.
* [ansiwrap](https://pypi.org/project/ansiwrap/) to perform the word wrapping.

# Commands

The following commands are available:

```
$ mdt --help
Usage: mdt [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  gallery  Shows a gallery with the available themes.
  show     Display the specified Markdown file.
  themes   Lists of available themes.
```

## Command `gallery`

Shows a sample markdown file with the application of all the available themes for demonstration purposes.

## Command `show`

Displays the specified markdown file with the default theme.

The theme can be selected by specifying the number among the ones available, or by using the `--theme-file` option to specify a custom theme.

```
$ mdt show --help
Usage: mdt show [OPTIONS] MDFILE

  Display the specified Markdown file.

Options:
  -i                 Interactive mode.
  --col INTEGER      Set the text width in number of columns.
  --rmargin INTEGER  Set the right margin.
  --theme INTEGER    Use a default theme by ID.
  --theme-file TEXT  Use the specified theme file.
  --help             Show this message and exit.
```

### Interactive mode

With the `-i` option, `mdt` is started in "interactive mode".
It then uses an internal pager which allows the scrolling of the text, and an intelligent word-wrapping.

Moreover, by pressing the `Tab` key, the pager moves to the next link in the markdown file.
Pressing `ENTER` on a link opens that link.
A link to a web page opens the browser.
A link to a file on the filesystem opens that file in `mdt`.
The history of opened files can be navigated using left and right arrows.

## Command `themes`

`mdt` comes with some sample themes.
This command lists the available themes.

More themes will be added.
Pull requests are welcome to provide new themes.

# Themimg

The themes are specified in a file with JSON format.
Examples are available in the `mdt/themes` directory.

The format is inspired by the one in the [Glamour Go library](https://github.com/charmbracelet/glamour/), with some additional fields to provide more options.

An example of theme file is:

```
{
  "document": {
    "prefix": "",
    "suffix": "",
    "margin": 2
  },
  "block_quote": {
    "prefix": "",
    "suffix": "",
    "color": "",
    "background_color": "",
    "bold": false,
    "underline": false,
    "blink": false
  },
  ...
```

where the styling items should be pretty straightforward to understand.

The available items that can be themed are: `document` `block_quote`, `paragraph`, `heading`, `h1`, `h2`, `h3`, `h4`, `h5`, `h6`, `strikethrough`, `emph`, `strong`, `item`, `list`, `link`, `selected_link`, `inline_code`, `block_code`.
