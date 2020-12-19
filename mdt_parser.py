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
class Applicationstate:
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
    file_manager = map(lambda x: x[1], Applicationstate.history)
    file_manager = list(file_manager)
    file_manager[Applicationstate.history_index] = '['+file_manager[Applicationstate.history_index]+']'
    line = ' '.join(file_manager)
    Applicationstate.root_container.get_children()[1].content.buffer.text = Applicationstate.history_template.format(line)


@bindings.add('left')
def go_back_history(event):
    """Go back to the previous file in the history."""
    Applicationstate.urls = {}
    if Applicationstate.history_index > 0:
        Applicationstate.history_index -= 1
    try:
        with open(Applicationstate.history[Applicationstate.history_index][0], 'r') as f:
            Applicationstate.p_text = f.read()
        Applicationstate.start_position = 0
        Applicationstate.current_link = -1
        return
    except:
        pass


@bindings.add('right')
def go_forward_history(event):
    Applicationstate.urls = {}
    if Applicationstate.history_index < len(Applicationstate.history)-1:
        Applicationstate.history_index += 1
    try:
        with open(Applicationstate.history[Applicationstate.history_index][0], 'r') as f:
            Applicationstate.p_text = f.read()
        Applicationstate.start_position = 0
        Applicationstate.current_link = -1
        return
    except:
        pass

@bindings.add('down')
def get_down(event):
    """Scroll down the file one line."""
    if Applicationstate.end_position < len(Applicationstate.rendered.split("\n")):
        Applicationstate.start_position += 1


@bindings.add('home')
def beginning_of_file(event):
    """Go to the beginning of the file."""
    Applicationstate.start_position = 0


@bindings.add('end')
def end_of_file(event):
    """Go to the end of file."""
    Applicationstate.start_position = len(Applicationstate.rendered.split('\n')) - Applicationstate.app.renderer.output.get_size()[0]

@bindings.add('up')
def get_up(event):
    """Scroll up the file one line."""
    if Applicationstate.start_position > 0:
        Applicationstate.start_position -= 1

@bindings.add('pageup')
def page_up(event):
    """Page up the file."""
    if Applicationstate.start_position > Applicationstate.app.renderer.output.get_size()[0]:
        Applicationstate.start_position -= Applicationstate.app.renderer.output.get_size()[0]
    else:
        Applicationstate.start_position = 0


@bindings.add('pagedown')
def page_down(event):
    """One page down the file."""
    if Applicationstate.start_position < len(Applicationstate.rendered.split('\n'))-2*Applicationstate.app.renderer.output.get_size()[0]:
        Applicationstate.start_position += Applicationstate.app.renderer.output.get_size()[0]
    else:
        Applicationstate.start_position = len(Applicationstate.rendered.split('\n')) - \
                                          Applicationstate.app.renderer.output.get_size()[0]

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
    if len(Applicationstate.urls) != 0:
        if Applicationstate.current_link < len(list(Applicationstate.urls))-1:
            Applicationstate.current_link += 1
            if Applicationstate.line_link_number[Applicationstate.current_link] - 1 + Applicationstate.app.renderer.output.get_size()[0] < len(Applicationstate.rendered.split('\n')):
                Applicationstate.start_position = Applicationstate.line_link_number[Applicationstate.current_link] - 1
            else:
                Applicationstate.start_position = len(Applicationstate.rendered.split('\n')) - Applicationstate.app.renderer.output.get_size()[0]
        if len(list(Applicationstate.urls)) == 1:
            Applicationstate.start_position = Applicationstate.line_link_number[0] - 1
        titolo = list(Applicationstate.urls)[Applicationstate.current_link]
        link = Applicationstate.urls[list(Applicationstate.urls)[Applicationstate.current_link]]
        Applicationstate.p_text = Applicationstate.p_text.replace('\007', '').replace('['+titolo+']('+link+')', '[\007'+titolo+']('+link+')')


@bindings.add('s-tab')
def link_before(event):
    """Go to the previous link."""
    if len(Applicationstate.urls) != 0:
        if Applicationstate.current_link > 0:
            Applicationstate.current_link -= 1
            #prendo la riga del link
            if Applicationstate.line_link_number[Applicationstate.current_link] - 1 + \
                    Applicationstate.app.renderer.output.get_size()[0] < len(Applicationstate.rendered.split('\n')):
                Applicationstate.start_position = Applicationstate.line_link_number[Applicationstate.current_link] - 1
            else:
                Applicationstate.start_position = len(Applicationstate.rendered.split('\n')) - \
                                                  Applicationstate.app.renderer.output.get_size()[0]
            titolo = list(Applicationstate.urls)[Applicationstate.current_link]
            link = Applicationstate.urls[list(Applicationstate.urls)[Applicationstate.current_link]]
            Applicationstate.p_text = Applicationstate.p_text.replace('\007', '').replace('[' + titolo + '](' + link + ')',
                                                                                          '[\007' + titolo + '](' + link + ')')

@bindings.add('enter')
def enter_link(event):
    """Open the selected link."""
    if len(Applicationstate.urls) > 0:
        link_ = Applicationstate.urls[list(Applicationstate.urls)[Applicationstate.current_link]]
        link_name = list(Applicationstate.urls)[Applicationstate.current_link]
        if (link_.endswith(".md")):
            Applicationstate.urls = {}
            Applicationstate.history_index += 1
            try:
                with open(link_, 'r') as f:
                    Applicationstate.p_text = f.read()
                Applicationstate.start_position = 0
                Applicationstate.current_link = -1
                tup = (link_, link_name)
                Applicationstate.history.append(tup)
                return
            except:
                pass
        else:
            try:
                webbrowser.open(Applicationstate.urls[list(Applicationstate.urls)[Applicationstate.current_link]])
            except:
                pass

def wrap_text(app):
    """Resize window every time (callable)."""
    Applicationstate.app = app
    fd = Document(Applicationstate.p_text)
    with MDTRenderer(dix=Applicationstate.custom_themes, global_ref=Applicationstate.urls, app=app) as render:
        Applicationstate.rendered = render.render(fd)
        Applicationstate.rendered = Applicationstate.custom_themes["document"]["prefix"]+Applicationstate.rendered+Applicationstate.custom_themes["document"]["suffix"]
        if Applicationstate.col != None:
            Applicationstate.rendered = '\n'.join(["\n".join(ansiwrap.wrap(l, Applicationstate.col -
                                                                           Applicationstate.custom_themes["document"][
                                                                               "margin"])) for l in
                                                   Applicationstate.rendered.split('\n')])
        else:
            Applicationstate.rendered = '\n'.join(["\n".join(ansiwrap.wrap(l, app.renderer.output.get_size()[1] -
                                                                           Applicationstate.custom_themes["document"][
                                                                                "margin"]-Applicationstate.rmargin)) for l in
                                                    Applicationstate.rendered.split('\n')])
        Applicationstate.rendered = textwrap.indent(Applicationstate.rendered,
                                                    " " * Applicationstate.custom_themes["document"]["margin"])

    Applicationstate.root_container.get_children()[0].content = FormattedTextControl(
        text=ANSI("\n".join(Applicationstate.rendered.split("\n")[Applicationstate.start_position:len(Applicationstate.rendered.split("\n"))])))
    Applicationstate.end_position = Applicationstate.start_position + app.renderer.output.get_size()[0]
    Applicationstate.line_link_number = []
    change_history_container()
    for w in (list(Applicationstate.urls)):
        count = 0
        for l in Applicationstate.rendered.split("\n"):
            count += 1
            if w in l:
                Applicationstate.line_link_number.append(count)

def show_gallery():
    Applicationstate.history.append(('', ''))
    for elem in sorted(os.listdir('themes')):
        theme_ = 'themes/' + elem
        with open(theme_) as j:
            Applicationstate.custom_themes = json.load(j)
        with open('sample_theme_text.md', 'r') as f:
            Applicationstate.p_text = f.read()
        ftc = FormattedTextControl(text=ANSI(Applicationstate.rendered))

        wind1 = Window(
            content=ftc,
            always_hide_cursor=True,
        )
        wind1.vertical_scroll = 1

        Applicationstate.root_container = HSplit(
            [
                wind1,

                TextArea(Applicationstate.history_template.format(Applicationstate.file_backwards,
                                                                  Applicationstate.file_forward), focusable=False),
            ])
        Applicationstate.app = Application(key_bindings=bindings, layout=Layout(Applicationstate.root_container),
                                           before_render=wrap_text)
        wrap_text(Applicationstate.app)
        print(elem+'\n')
        print_formatted_text(ANSI(Applicationstate.rendered))


def show_theme_list():
    styles = zip(range(1, len(os.listdir('themes'))+1), sorted(os.listdir('themes')))
    for n, l in styles:
        print('{} : {}'.format(n, l))


def run(interactive):
    ftc = FormattedTextControl(text=ANSI(Applicationstate.rendered))

    wind1 = Window(
        content=ftc,
        always_hide_cursor=True,
    )
    wind1.vertical_scroll = 1

    Applicationstate.root_container = HSplit(
        [
            wind1,

            TextArea(Applicationstate.history_template.format(Applicationstate.file_backwards, Applicationstate.file_forward), focusable=False),
        ])
    Applicationstate.app = Application(key_bindings=bindings, layout=Layout(Applicationstate.root_container),
                                       before_render=wrap_text)
    wrap_text(Applicationstate.app)
    if interactive == False:
        print_formatted_text(ANSI(Applicationstate.rendered))
    else:
        Applicationstate.app.run()


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


@click.command()
@click.argument('mdfile', required=False)
@click.option('--gallery', help='Print a demo gallery of the available themes.', is_flag=True)
@click.option('-i', help='Interactive mode.', is_flag=True)
@click.option('-l', help='List all the default themes.', is_flag=True)
@click.option('--col', callback=check_col_arg, help='Set the text width in number of columns.', type=int)
@click.option('--rmargin', callback=check_rmargin_arg, help='Set the right right margin.', type=int, default=0)
@click.option('--theme', default=1, callback=check_theme_arg, help='Choose a default theme by ID.', type=int)
@click.option('--theme-file', help='Choose a theme file.')
def mdt(mdfile, theme, gallery, i, l, col=None, rmargin=0, theme_file=None):
    """Main function."""
    if col != None and rmargin != 0:
        print("The options --col and --rmargin can not be used at the same time.")
        exit(1)
    if gallery == True:
        show_gallery()
        return
    if l == True:
        show_theme_list()
        return

    theme_ = 'themes/' + sorted(os.listdir('themes'))[0]
    if theme is not None:
        theme_ = 'themes/' + sorted(os.listdir('themes'))[theme-1]
    if theme_file is not None:
        theme_ = theme_file

    try:
        with open(theme_) as j:
            Applicationstate.custom_themes = json.load(j)
    except:
        print("Theme file {} not found.".format(theme_))
        exit(1)
    if mdfile == None:
        print("Markdown file name required.")
        exit(1)

    try:
        with open(mdfile, 'r') as f:
            Applicationstate.p_text = f.read()
    except:
        print("Markdown file {} not found.".format(mdfile))
        exit(1)
    Applicationstate.history.append((mdfile, mdfile))
    Applicationstate.max_h = len(Applicationstate.rendered.split("\n"))
    Applicationstate.col = col
    Applicationstate.rmargin = rmargin
    run(i)


def main():
    mdt()


if __name__ == '__main__':
    main()
