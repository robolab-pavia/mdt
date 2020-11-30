import json
import webbrowser
from prompt_toolkit.widgets import TextArea
from plain_render import Plain_Renderer
import click
import re
from prompt_toolkit.data_structures import Point
from prompt_toolkit import Application, HTML, print_formatted_text
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from mdt_render import HTMLRenderer
from mistletoe import Document

#Global variable


# Global key bindings.
bindings = KeyBindings()


#class for global variable
class Applicationstate():
    max_h = 0
    #variable for vertical movements
    v = 0
    #variablefor horizontal movement
    h = 0

    #reference text
    plain_text_=""

    #flag for scroll
    just_got_up = True
    just_got_down = False

    app = None
    root_container = None

    text_len_ = 0

    #name text variable
    named_text = ""

    #iter in md_files
    md_files = []
    md_files_iter = 0
    is_duplicate = False

    #choose an old files
    file_chooser = 0

    #urls vector
    urls = None
    link_count = -1


def get_cursor():
    return Point(Applicationstate.h, Applicationstate.v)

@bindings.add('b')
def go_back(event):
    try:
        with open(Applicationstate.md_files[Applicationstate.md_files_iter]) as f:
            fd = Document(f.read())
            with HTMLRenderer() as render:
                rendered = render.render(fd)
            with Plain_Renderer() as render:
                Applicationstate.plain_text_ = render.render(fd)
                Applicationstate.v, Applicationstate.h = (0, 0)
                Applicationstate.max_h = len(rendered.split("\n"))
                Applicationstate.md_files.append(Applicationstate.named_text)
                Applicationstate.is_duplicate = False
                for name in Applicationstate.md_files:
                    if Applicationstate.named_text == name:
                        Applicationstate.is_duplicate = True
                    else:
                        continue
                if Applicationstate.is_duplicate == False:
                    Applicationstate.named_text = Applicationstate.md_files[Applicationstate.md_files_iter]
                Applicationstate.urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', rendered)
                Applicationstate.root_container.get_children()[0].content = FormattedTextControl(text=HTML(rendered),
                                                                                                 get_cursor_position=get_cursor)


    except:
        pass

@bindings.add('right')
def _(event):
    if Applicationstate.md_files_iter < len(Applicationstate.md_files) and len(Applicationstate.md_files) >= 0:
        Applicationstate.md_files_iter += 1

@bindings.add('left')
def _(event):
    if Applicationstate.md_files_iter < len(Applicationstate.md_files) and len(Applicationstate.md_files) >= 0:
        Applicationstate.md_files_iter -= 1


@bindings.add('down')
def get_down(event):
    if Applicationstate.just_got_up:
        Applicationstate.v += Applicationstate.app.renderer.output.get_size()[0]
        Applicationstate.just_got_up = False
        Applicationstate.just_got_down = True
    if Applicationstate.just_got_down:
        if Applicationstate.v == Applicationstate.max_h-2:
            Applicationstate.v = Applicationstate.max_h-2
        else:
            Applicationstate.v += 1

@bindings.add('up')
def get_up(event):
    if Applicationstate.just_got_down:
        Applicationstate.v -= Applicationstate.app.renderer.output.get_size()[0]
        Applicationstate.just_got_up = True
        Applicationstate.just_got_down = False
    if Applicationstate.just_got_up:
        if Applicationstate.v == 0:
            Applicationstate.v = 0
        else:
            Applicationstate.v -= 1


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
    if Applicationstate.link_count + 1 < len(Applicationstate.urls):
        Applicationstate.link_count += 1
        Applicationstate.v = 0
        Applicationstate.root_container.get_children()[1].content.buffer.text = Applicationstate.urls[Applicationstate.link_count]
        word = Applicationstate.urls[Applicationstate.link_count]
        splitted_text = Applicationstate.plain_text_.split('\n')
        for vec in splitted_text:
            if word in vec:
                return
            else:
                if Applicationstate.v <= Applicationstate.max_h-2:
                    Applicationstate.v += 1

@bindings.add('s-tab')
def link_before(event):
    if Applicationstate.link_count > 0:
        Applicationstate.link_count -= 1
        Applicationstate.root_container.get_children()[1].content.buffer.text = Applicationstate.urls[Applicationstate.link_count]
        word = Applicationstate.urls[Applicationstate.link_count]
        Applicationstate.v = 0
        splitted_text = Applicationstate.plain_text_.split('\n')
        for vec in splitted_text:
            if word in vec:
                return
            else:
                if Applicationstate.v <= Applicationstate.max_h - 2:
                    Applicationstate.v += 1

@bindings.add('enter')
def enter_link(event):
    link_ = Applicationstate.urls[Applicationstate.link_count]
    if(link_.endswith(".md")):
        Applicationstate.md_files.append(Applicationstate.named_text)
        try:
            with open(link_) as f:
                fd = Document(f.read())
                with HTMLRenderer() as render:
                    rendered = render.render(fd)
                with Plain_Renderer() as render:
                    Applicationstate.plain_text_ = render.render(fd)
                Applicationstate.v, Applicationstate.h = (0, 0)
                Applicationstate.named_text = link_
                Applicationstate.max_h = len(rendered.split("\n"))
                Applicationstate.link_count = - 1
                Applicationstate.urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', rendered)
                Applicationstate.root_container.get_children()[0].content = FormattedTextControl(text=HTML(rendered),
                                                                               get_cursor_position=get_cursor)
                return
        except:
            pass
    else:
        try:
            webbrowser.open(Applicationstate.urls[Applicationstate.link_count])
        except:
            pass


# creo il parser per il terminale
@click.command()
@click.argument('text',  required=True)
@click.option('--theme', default=0, help='theme you want to use')
@click.option('--i', default=False, help='Interactive mode')

def mdt(text, theme, i):

    Applicationstate.named_text = text

    with open('theme.json') as j:
        custom_themes = json.load(j)


    with open(text, 'r') as f:
        fd = Document(f.read())
        with HTMLRenderer() as render:
            rendered = render.render(fd)
        with Plain_Renderer() as render:
            Applicationstate.plain_text_ = render.render(fd)

        #text theme
        style = Style.from_dict(custom_themes)

    if i==False:
        print_formatted_text(HTML(rendered), style=style)

    else:
        Applicationstate.max_h = len(rendered.split("\n"))

        Applicationstate.urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', rendered)

        ftc = FormattedTextControl(text=HTML(rendered), get_cursor_position=get_cursor)
        print(Applicationstate.plain_text_)

        wind1 = Window(
                    content=ftc,
                    wrap_lines=True,
                    always_hide_cursor=True,
                )
        wind1.vertical_scroll = 1

        Applicationstate.root_container =HSplit(
            [
                wind1,

                TextArea('Tab to choose link:', focusable=False),
                                                 ])
        print(Applicationstate.plain_text_.split('\n')[0])
        Applicationstate.app = Application(key_bindings=bindings, layout=Layout(Applicationstate.root_container), style=style)
        print(Applicationstate.plain_text_.split('\n'))
        Applicationstate.app.run()