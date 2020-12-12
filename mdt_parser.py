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
    rmargin = None

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
    history_template = 'file_backwards:"{}"  file_forward:"{}"'
    # urls vector
    urls = {}
    line_link_number = []

def change_history_container():
    if len(Applicationstate.history) > 1 and Applicationstate.history_index > 0:
        Applicationstate.file_backwards = Applicationstate.history[Applicationstate.history_index-1][1]
    if Applicationstate.history_index < len(Applicationstate.history)-1:
        Applicationstate.file_forward = Applicationstate.history[Applicationstate.history_index+1][1]
    if Applicationstate.history_index == len(Applicationstate.history)-1:
        Applicationstate.file_forward = ""
    if Applicationstate.history_index == 0:
        Applicationstate.file_backwards = ""
    Applicationstate.root_container.get_children()[1].content.buffer.text = Applicationstate.history_template.format(Applicationstate.file_backwards, Applicationstate.file_forward)


#go back in file.md history
@bindings.add('left')
def go_back_history(event):
    Applicationstate.urls = {}
    if Applicationstate.history_index > 0:
        Applicationstate.history_index -= 1
    try:
        with open(Applicationstate.history[Applicationstate.history_index][0], 'r') as f:
            Applicationstate.p_text = f.read()
        Applicationstate.start_position = 0
        Applicationstate.current_link = -1
        change_history_container()
        return
    except:
        pass

@bindings.add('right')
def go_back_history(event):
    Applicationstate.urls = {}
    if Applicationstate.history_index < len(Applicationstate.history)-1:
        Applicationstate.history_index += 1
    try:
        with open(Applicationstate.history[Applicationstate.history_index][0], 'r') as f:
            Applicationstate.p_text = f.read()
        Applicationstate.start_position = 0
        Applicationstate.current_link = -1
        change_history_container()
        return
    except:
        pass

# scroll down the file
@bindings.add('down')
def get_down(event):
    if Applicationstate.end_position < len(Applicationstate.rendered.split("\n")):
        Applicationstate.start_position += 1

# go to the beginning of the file
@bindings.add('home')
def beginning_of_file(event):
    Applicationstate.start_position = 0

# go to the end of the file
@bindings.add('end')
def end_of_file(event):
    Applicationstate.start_position = len(Applicationstate.rendered.split('\n')) - Applicationstate.app.renderer.output.get_size()[0]

# scroll up the file
@bindings.add('up')
def get_up(event):
    if Applicationstate.start_position > 0:
        Applicationstate.start_position -= 1

# page up the file
@bindings.add('pageup')
def page_up(event):
    if Applicationstate.start_position > Applicationstate.app.renderer.output.get_size()[0]:
        Applicationstate.start_position -= Applicationstate.app.renderer.output.get_size()[0]
    else:
        Applicationstate.start_position = 0

# page down the file
@bindings.add('pagedown')
def page_down(event):
    if Applicationstate.start_position < len(Applicationstate.rendered.split('\n'))-Applicationstate.app.renderer.output.get_size()[0]:
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

# go to the next link
@bindings.add('tab')
def link_after(event):
    if len(Applicationstate.urls) != 0:
        if Applicationstate.current_link < len(list(Applicationstate.urls))-1:
            Applicationstate.current_link += 1
            #Applicationstate.root_container.get_children()[1].content.buffer.text = Applicationstate.urls[list(Applicationstate.urls)[Applicationstate.current_link]]
            Applicationstate.start_position = Applicationstate.line_link_number[Applicationstate.current_link] - 1
        if len(list(Applicationstate.urls)) == 1:
            Applicationstate.start_position = Applicationstate.line_link_number[0] - 1
        titolo = list(Applicationstate.urls)[Applicationstate.current_link]
        link = Applicationstate.urls[list(Applicationstate.urls)[Applicationstate.current_link]]
        Applicationstate.p_text = Applicationstate.p_text.replace('\007', '').replace('['+titolo+']('+link+')', '[\007'+titolo+']('+link+')')


# go to the previous link
@bindings.add('s-tab')
def link_before(event):
    if len(Applicationstate.urls) != 0:
        if Applicationstate.current_link > 0:
            Applicationstate.current_link -= 1
            #prendo la riga del link
            Applicationstate.start_position = Applicationstate.line_link_number[Applicationstate.current_link] - 1
            titolo = list(Applicationstate.urls)[Applicationstate.current_link]
            link = Applicationstate.urls[list(Applicationstate.urls)[Applicationstate.current_link]]
            Applicationstate.p_text = Applicationstate.p_text.replace('\007', '').replace('[' + titolo + '](' + link + ')',
                                                                                          '[\007' + titolo + '](' + link + ')')

# open the choosen link
@bindings.add('enter')
def enter_link(event):
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
            change_history_container()
            return
        except:
            pass
    else:
        try:
            webbrowser.open(Applicationstate.urls[list(Applicationstate.urls)[Applicationstate.current_link]])
        except:
            pass

# resize window every time (callable)
def wrap_text(app):
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
    for w in (list(Applicationstate.urls)):
        count = 0
        for l in Applicationstate.rendered.split("\n"):
            count += 1
            if w in l:
                Applicationstate.line_link_number.append(count)

# main
@click.command()
@click.argument('text', required=True)
@click.option('--theme', default=0, help='theme you want to use')
@click.option('-i', help='Interactive mode', is_flag=True)
@click.option('-col', help='Choose the last column width', type=int)
@click.option('-rmargin', help='Right margin', type=int, default=0)
def mdt(text, theme, i, col=None, rmargin=0):
    if col != None and rmargin != 0:
        raise Exception("You can't put -col and -rmargin attribute!")

    with open('theme.json') as j:
        Applicationstate.custom_themes = json.load(j)

    with open(text, 'r') as f:
        Applicationstate.p_text = f.read()
    Applicationstate.history.append((text, text))
    Applicationstate.max_h = len(Applicationstate.rendered.split("\n"))
    Applicationstate.col = col
    Applicationstate.rmargin = rmargin

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
    if i == False:
        print_formatted_text(ANSI(Applicationstate.rendered))
    else:
        Applicationstate.app.run()
