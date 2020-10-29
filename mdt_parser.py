import mistletoe
import argparse
import json
from rich.console import Console
from rich.theme import Theme
from mdt_render import MDTRenderer
from mistletoe import Document
# creo il parser per il terminale


parser = argparse.ArgumentParser(description="Inserire il file markdown da tradurre")
parser.add_argument('text', type=str, help="file markdown")
parser.add_argument('integers', type=int, help="choose the theme", default=0)
args = parser.parse_args()


with open('theme.json') as j:
    custom_themes = json.load(j)
    if args.integers == 0:
        custom_theme = Theme(custom_themes[0])
    else:
        custom_theme = Theme(custom_themes[1])

with open(args.text, 'r') as f:
    with MDTRenderer() as render:
        rendered = render.render(Document(f))

console = Console(theme=custom_theme)
console.print(rendered)