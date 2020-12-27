"""
    <Markdown file reader from terminal.>
    Copyright (C) <2020>  <Catena Andrea, Facchinetti Tullio, Benetti Guido>
"""
"""
    Markdown in terminal is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Markdown in terminal is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Markdown in terminal.  If not, see <http://www.gnu.org/licenses/>.
"""
import json
import textwrap
import webbrowser
import ansiwrap
from prompt_toolkit.widgets import TextArea
import click
from prompt_toolkit import Application, HTML, print_formatted_text, ANSI
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from mdt_render import MDTRenderer
from mistletoe import Document
import os


# Global key bindings.
bindings = KeyBindings()


# class for global variable
class AppState:
    max_h = 0
    start_position = 0
    end_position = 0

    custom_themes = None

    #margin
    col = None
    rmargin = 0

    # reference text
    plain_text_ = ""
    p_text = None

    # rendered text
    rendered = ""

    # link counter
    current_link = -1

    app = None
    root_container = None

    width = 40

    text_len_ = 0

    # name text variable
    named_text = ""

    # History file manager
    history = []
    history_index = 0
    file_backwards = ""
    file_forward = ""
    history_template = ' mdt: {}'
    # urls vector
    urls = {}
    line_link_number = []


def change_history_container():
    file_manager = []
    file_manager = map(lambda x: x[1], AppState.history)
    file_manager = list(file_manager)
    file_manager[AppState.history_index] = '[' + file_manager[AppState.history_index] + ']'
    line = ' '.join(file_manager)
    AppState.root_container.get_children()[1].content.buffer.text = AppState.history_template.format(line)


@bindings.add('left')
def go_back_history(event):
    """Go back to the previous file in the history."""
    AppState.urls = {}
    if AppState.history_index > 0:
        AppState.history_index -= 1
    try:
        with open(AppState.history[AppState.history_index][0], 'r') as f:
            AppState.p_text = f.read()
        AppState.start_position = 0
        AppState.current_link = -1
        return
    except:
        pass


@bindings.add('right')
def go_forward_history(event):
    AppState.urls = {}
    if AppState.history_index < len(AppState.history)-1:
        AppState.history_index += 1
    try:
        with open(AppState.history[AppState.history_index][0], 'r') as f:
            AppState.p_text = f.read()
        AppState.start_position = 0
        AppState.current_link = -1
        return
    except:
        pass

@bindings.add('down')
def get_down(event):
    """Scroll down the file one line."""
    if AppState.end_position < len(AppState.rendered.split("\n")):
        AppState.start_position += 1


@bindings.add('home')
def beginning_of_file(event):
    """Go to the beginning of the file."""
    AppState.start_position = 0


@bindings.add('end')
def end_of_file(event):
    """Go to the end of file."""
    AppState.start_position = len(AppState.rendered.split('\n')) - AppState.app.renderer.output.get_size()[0]

@bindings.add('up')
def get_up(event):
    """Scroll up the file one line."""
    if AppState.start_position > 0:
        AppState.start_position -= 1

@bindings.add('pageup')
def page_up(event):
    """Page up the file."""
    if AppState.start_position > AppState.app.renderer.output.get_size()[0]:
        AppState.start_position -= AppState.app.renderer.output.get_size()[0]
    else:
        AppState.start_position = 0


@bindings.add('pagedown')
def page_down(event):
    """One page down the file."""
    if AppState.start_position < len(AppState.rendered.split('\n'))-2*AppState.app.renderer.output.get_size()[0]:
        AppState.start_position += AppState.app.renderer.output.get_size()[0]
    else:
        AppState.start_position = len(AppState.rendered.split('\n')) - \
                                  AppState.app.renderer.output.get_size()[0]

# quit the application
@bindings.add('q')
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.
    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()


@bindings.add('tab')
def link_after(event):
    """Go to the next link."""
    if AppState.current_link >= len(list(AppState.urls))-1:
        AppState.current_link = -1
    if len(AppState.urls) != 0:
        if AppState.current_link < len(list(AppState.urls))-1:
            AppState.current_link += 1
            if AppState.line_link_number[AppState.current_link] - 1 + AppState.app.renderer.output.get_size()[0] < len(AppState.rendered.split('\n')):
                AppState.start_position = AppState.line_link_number[AppState.current_link] - 1
            else:
                AppState.start_position = len(AppState.rendered.split('\n')) - AppState.app.renderer.output.get_size()[0]
        if len(list(AppState.urls)) == 1:
            AppState.start_position = AppState.line_link_number[0] - 1
        titolo = list(AppState.urls)[AppState.current_link]
        link = AppState.urls[list(AppState.urls)[AppState.current_link]]
        AppState.p_text = AppState.p_text.replace('\007', '').replace('[' + titolo + '](' + link + ')', '[\007' + titolo + '](' + link + ')')


@bindings.add('s-tab')
def link_before(event):
    """Go to the previous link."""
    if len(AppState.urls) != 0:
        if AppState.current_link > 0:
            AppState.current_link -= 1
            #prendo la riga del link
            if AppState.line_link_number[AppState.current_link] - 1 + \
                    AppState.app.renderer.output.get_size()[0] < len(AppState.rendered.split('\n')):
                AppState.start_position = AppState.line_link_number[AppState.current_link] - 1
            else:
                AppState.start_position = len(AppState.rendered.split('\n')) - \
                                          AppState.app.renderer.output.get_size()[0]
            titolo = list(AppState.urls)[AppState.current_link]
            link = AppState.urls[list(AppState.urls)[AppState.current_link]]
            AppState.p_text = AppState.p_text.replace('\007', '').replace('[' + titolo + '](' + link + ')',
                                                                                          '[\007' + titolo + '](' + link + ')')

@bindings.add('enter')
def enter_link(event):
    """Open the selected link."""
    if len(AppState.urls) > 0:
        link_ = AppState.urls[list(AppState.urls)[AppState.current_link]]
        link_name = list(AppState.urls)[AppState.current_link]
        if (link_.endswith(".md")):
            AppState.urls = {}
            AppState.history_index += 1
            try:
                with open(link_, 'r') as f:
                    AppState.p_text = f.read()
                AppState.start_position = 0
                AppState.current_link = -1
                tup = (link_, link_name)
                AppState.history.append(tup)
                return
            except:
                pass
        else:
            try:
                webbrowser.open(AppState.urls[list(AppState.urls)[AppState.current_link]])
            except:
                pass

def wrap_text(app):
    """Resize window every time (callable)."""
    AppState.app = app
    fd = Document(AppState.p_text)
    with MDTRenderer(dix=AppState.custom_themes, global_ref=AppState.urls, app=app) as render:
        AppState.rendered = render.render(fd)
        AppState.rendered = AppState.custom_themes["document"]["prefix"] + AppState.rendered + AppState.custom_themes["document"]["suffix"]
        if AppState.col != None:
            AppState.rendered = '\n'.join(["\n".join(ansiwrap.wrap(l, AppState.col -
                                                                   AppState.custom_themes["document"][
                                                                               "margin"])) for l in
                                           AppState.rendered.split('\n')])
        else:
            AppState.rendered = '\n'.join(["\n".join(ansiwrap.wrap(l, app.renderer.output.get_size()[1] -
                                                                   AppState.custom_themes["document"][
                                                                                "margin"] - AppState.rmargin)) for l in
                                           AppState.rendered.split('\n')])
        AppState.rendered = textwrap.indent(AppState.rendered,
                                                    " " * AppState.custom_themes["document"]["margin"])

    AppState.root_container.get_children()[0].content = FormattedTextControl(
        text=ANSI("\n".join(AppState.rendered.split("\n")[AppState.start_position:len(AppState.rendered.split("\n"))])))
    AppState.end_position = AppState.start_position + app.renderer.output.get_size()[0]
    AppState.line_link_number = []
    change_history_container()
    for w in (list(AppState.urls)):
        count = 0
        for l in AppState.rendered.split("\n"):
            count += 1
            if w in l:
                AppState.line_link_number.append(count)

def show_gallery():
    AppState.history.append(('', ''))
    for elem in sorted(os.listdir('themes')):
        theme_ = 'themes/' + elem
        with open(theme_) as j:
            AppState.custom_themes = json.load(j)
        with open('sample_theme_text.md', 'r') as f:
            AppState.p_text = f.read()
        ftc = FormattedTextControl(text=ANSI(AppState.rendered))

        wind1 = Window(
            content=ftc,
            always_hide_cursor=True,
        )
        wind1.vertical_scroll = 1

        AppState.root_container = HSplit(
            [
                wind1,

                TextArea(AppState.history_template.format(AppState.file_backwards,
                                                          AppState.file_forward), focusable=False),
            ])
        AppState.app = Application(key_bindings=bindings, layout=Layout(AppState.root_container),
                                   before_render=wrap_text)
        wrap_text(AppState.app)
        print(elem+'\n')
        print_formatted_text(ANSI(AppState.rendered))


def show_theme_list():
    styles = zip(range(1, len(os.listdir('themes'))+1), sorted(os.listdir('themes')))
    for n, l in styles:
        print('{} : {}'.format(n, l))


def run(interactive):
    ftc = FormattedTextControl(text=ANSI(AppState.rendered))

    wind1 = Window(
        content=ftc,
        always_hide_cursor=True,
    )
    wind1.vertical_scroll = 1

    AppState.root_container = HSplit(
        [
            wind1,

            TextArea(AppState.history_template.format(AppState.file_backwards, AppState.file_forward), focusable=False),
        ])
    AppState.app = Application(key_bindings=bindings, layout=Layout(AppState.root_container),
                               before_render=wrap_text)
    wrap_text(AppState.app)
    if interactive == False:
        print_formatted_text(ANSI(AppState.rendered))
    else:
        AppState.app.run()


def check_theme_arg(ctx, param, value):
    """Callback for checking the value of the theme ID."""
    if value <= 0:
        raise click.BadParameter('negative value {}'.format(value))
    n_themes = len(os.listdir('themes'))
    if value > n_themes:
        raise click.BadParameter("required theme ID in [1..{}], given {}".format(n_themes, value))
    return value


def check_col_arg(ctx, param, value):
    """Callback for checking the value of the columns."""
    if value is None:
        return value
    if value <= 0:
        raise click.BadParameter('non-positive value {}'.format(value))
    return value


def check_rmargin_arg(ctx, param, value):
    """Callback for checking the value of the right margin."""
    if value is None:
        return value
    if value < 0:
        raise click.BadParameter('negative value {}'.format(value))
    return value


@click.group()
def cli():
    pass


@cli.command(name='show', help='Display the specified Markdown file.')
@click.argument('mdfile', required=True)
@click.option('-i', help='Interactive mode.', is_flag=True)
@click.option('--col', callback=check_col_arg, help='Set the text width in number of columns.', type=int)
@click.option('--rmargin', callback=check_rmargin_arg, help='Set the right margin.', type=int, default=0)
@click.option('--theme', default=1, callback=check_theme_arg, help='Use a default theme by ID.', type=int)
@click.option('--theme-file', help='Use the specified theme file.')
def cmd_show(mdfile, i=True, col=None, rmargin=0, theme=None, theme_file=None):
    AppState.col = col
    AppState.rmargin = rmargin
    theme_ = 'themes/' + sorted(os.listdir('themes'))[0]
    if theme is not None:
        theme_ = 'themes/' + sorted(os.listdir('themes'))[theme-1]
    if theme_file is not None:
        theme_ = theme_file
    try:
        with open(theme_) as j:
            AppState.custom_themes = json.load(j)
    except:
        print("Theme file {} not found.".format(theme_))
        exit(1)
    if mdfile == None:
        print("Markdown file name required.")
        exit(1)
    try:
        with open(mdfile, 'r') as f:
            AppState.p_text = f.read()
    except:
        print("Markdown file {} not found.".format(mdfile))
        exit(1)
    AppState.history.append((mdfile, mdfile))
    AppState.max_h = len(AppState.rendered.split("\n"))
    run(i)


@cli.command(name='gallery', help='Shows a gallery with the available themes.')
@click.option('--col', callback=check_col_arg, help='Set the text width in number of columns.', type=int)
@click.option('--rmargin', callback=check_rmargin_arg, help='Set the right right margin.', type=int, default=0)
def cmd_gallery(col=None, rmargin=0):
    AppState.col = col
    AppState.rmargin = rmargin
    if col != None and rmargin != 0:
        print("The options --col and --rmargin can not be used at the same time.")
        exit(1)
    show_gallery()


@cli.command(name='themes', help='Lists of available themes.')
def cmd_themes():
    show_theme_list()


def main():
    cli.add_command(cmd_show)
    cli.add_command(cmd_gallery)
    cli.add_command(cmd_themes)
    cli()


if __name__ == '__main__':
    main()
