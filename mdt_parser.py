
import mistletoe
import json
from plain_render import Plain_Renderer
import click
from prompt_toolkit.formatted_text import to_formatted_text, fragment_list_to_text, FormattedText
from prompt_toolkit.layout import CompletionsMenu, Container, Dimension
from prompt_toolkit.layout.processors import Processor, Transformation
from prompt_toolkit.lexers import DynamicLexer, PygmentsLexer
from prompt_toolkit.widgets import TextArea, SearchToolbar, MenuItem, MenuContainer, Frame
from prompt_toolkit.enums import DEFAULT_BUFFER
import handler_view
from prompt_toolkit.data_structures import Point
from prompt_toolkit import Application, HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import print_formatted_text
from prompt_toolkit.styles import Style
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import VSplit, Window, HSplit, ConditionalContainer, Float
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout import ScrollOffsets
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

    old_file = None
    this_file = None

    root_container = None

    text_len_ = 0


def get_cursor():
    return Point(Applicationstate.h, Applicationstate.v)

@bindings.add('down')
def get_down(event):
    if Applicationstate.v > Applicationstate.max_h-2: Applicationstate.v -= 1
    if Applicationstate.h != 0: Applicationstate.h = 0
    Applicationstate.v += 1


@bindings.add('up')
def get_up(event):
    if Applicationstate.v < 0: Applicationstate.v+=1
    Applicationstate.v -= 1


@bindings.add('right')
def get_right(event):
    Applicationstate.h += 1


@bindings.add('left')
def get_left(event):
    if Applicationstate.h == 0: Applicationstate.h +=1
    Applicationstate.h -= 1

@bindings.add('c-b')
def go_back(event):
    if(Applicationstate.old_file == None): return

    with open(Applicationstate.old_file) as f:
        fd = Document(f.read())
        with HTMLRenderer() as render:
            rendered = render.render(fd)
        with Plain_Renderer() as render:
            Applicationstate.plain_text_ = render.render(fd)
    Applicationstate.v, Applicationstate.h = (0, 0)
    Applicationstate.max_h = len(rendered.split("\n"))
    Applicationstate.root_container.content = FormattedTextControl(text=HTML(rendered),get_cursor_position=get_cursor)
    tmp = Applicationstate.old_file
    Applicationstate.old_file = Applicationstate.this_file
    Applicationstate.this_file = tmp


@bindings.add('c-o')
def open_filemd(event):
    line = Applicationstate.plain_text_.split("\n")[Applicationstate.v]
    lst_words = line[Applicationstate.h:].split(" ")
    for word in lst_words:
        if word.endswith(".md"):
            word_2 = word.replace(" ","")
            try:
                with open(word_2) as f:
                    fd = Document(f.read())
                    with HTMLRenderer() as render:
                        rendered = render.render(fd)
                    with Plain_Renderer() as render:
                        Applicationstate.plain_text_ = render.render(fd)
                    Applicationstate.v, Applicationstate.h = (0,0)
                    Applicationstate.max_h = len(rendered.split("\n"))
                    Applicationstate.root_container.content = FormattedTextControl(text=HTML(rendered), get_cursor_position=get_cursor)
                    Applicationstate.old_file = Applicationstate.this_file
                    Applicationstate.this_file = word_2
                    return
            except:
                pass


@bindings.add('c-q')
def exit_(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    event.app.exit()

# creo il parser per il terminale
@click.command()
@click.argument('text',  required=True)
@click.option('--theme', default=0, help='theme you want to use')
def mdt(text, theme):

    with open('theme.json') as j:
        custom_themes = json.load(j)


    with open(text, 'r') as f:
        fd = Document(f.read())
        with HTMLRenderer() as render:
            rendered = render.render(fd)
        with Plain_Renderer() as render:
            Applicationstate.plain_text_= render.render(fd)

    Applicationstate.max_h = len(rendered.split("\n"))
    Applicationstate.old_file = text
    Applicationstate.this_file = text


    style = Style.from_dict(custom_themes)

    ftc = FormattedTextControl(text=HTML(rendered), get_cursor_position=get_cursor)

    Applicationstate.root_container = Window(content=ftc, wrap_lines=True)

    app = Application(key_bindings=bindings, layout=Layout(Applicationstate.root_container), style=style)
    app.run()
