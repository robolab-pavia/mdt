"""
    <Markdown file reader from terminal.>
    Copyright (C) <2020>  <Catena Andrea, Facchinetti Tullio, Benetti Guido>

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
"""
mdt renderer for mistletoe.
"""
import click
from mistletoe.base_renderer import BaseRenderer


def unpack_style_fields(item):
    pre = item.get("prefix", "")
    suf = item.get("suffix", "")
    fg = item.get("color", "")
    bg = item.get("background_color", "")
    bold = item.get("bold", "")
    ul = item.get("underline", "")
    blink = item.get("blink", "")
    return pre, suf, fg, bg, bold, ul, blink


class MDTRenderer(BaseRenderer):
    """
    mdt renderer class.
    See mistletoe.base_renderer module for more info.
    """
    def __init__(self, *extras, dix, global_ref, app):
        self.dix = dix
        self.global_ref = global_ref
        self.app = app
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        self._suppress_ptag_stack = [False]
        super().__init__()
        # html.entities.html5 includes entitydefs not ending with ';',
        # CommonMark seems to hate them, so...

    def __exit__(self, *args):
        super().__exit__(*args)

    def render_to_plain(self, token):
        if hasattr(token, 'children'):
            inner = [self.render_to_plain(child) for child in token.children]
            return ''.join(inner)
        return token.content

    def format_inline_text(self, key):
        pre, suf, fg, bg, bold, ul, blink = unpack_style_fields(self.dix[key])
        template = click.style(pre + "{}" + suf, bg=bg, fg=fg, bold=bold, underline=ul, blink=blink)
        return template

    def render_strong(self, token):
        template = self.format_inline_text("strong")
        return template.format(self.render_inner(token))

    def render_emphasis(self, token):
        template = self.format_inline_text("emph")
        return template.format(self.render_inner(token))

    def render_inline_code(self, token):
        template = self.format_inline_text("inline_code")
        inner = token.children[0].content
        return template.format(inner)

    def render_strikethrough(self, token):
        template = self.format_inline_text("strikethrough")
        return template.format(self.render_inner(token))

    def render_link(self, token):
        target = token.target
        inner = self.render_inner(token)
        if inner.startswith('\007'):
            inner = inner.replace('\007', '')
            pre, suf, fg, bg, bold, ul, blink = unpack_style_fields(self.dix["selected_link"])
        else:
            pre, suf, fg, bg, bold, ul, blink = unpack_style_fields(self.dix["link"])
        template = click.style(pre + "{inner}" + suf, bg=bg, fg=fg, bold=bold, underline=ul, blink=blink)
        self.global_ref.update({inner: target})
        return template.format(target=target, inner=inner)

    def render_heading(self, token):
        key = "h" + str(token.level)
        pre_1, suf_1, fg_1, bg_1, bold_1, ul_1, blink_1 = unpack_style_fields(self.dix["heading"])
        pre_2, suf_2, fg_2, bg_2, bold_2, ul_2, blink_2 = unpack_style_fields(self.dix[key])
        pre = pre_2 if pre_2 != "" else pre_1
        suf = suf_2 if suf_2 != "" else suf_1
        fg = fg_2 if fg_2 != "" else fg_1
        bg = bg_2 if bg_2 != "" else bg_1
        bold = bold_2 if bold_2 != "" else bold_1
        ul = ul_2 if ul_2 != "" else ul_1
        blink = blink_2 if blink_2 != "" else blink_1
        template = click.style(pre + "{inner}" + suf, bg=bg, fg=fg, bold=bold, underline=ul, blink=blink)
        inner = self.render_inner(token)
        return template.format(inner=inner)

    def render_quote(self, token):
        elements = [""]
        self._suppress_ptag_stack.append(False)
        elements.extend([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        elements.append("")
        pre, suf, fg, bg, bold, ul, blink = unpack_style_fields(self.dix["block_quote"])
        return click.style(pre + ''.join(elements) + suf, bg=bg, fg=fg, bold=bold, underline=ul, blink=blink)

    def render_paragraph(self, token):
        if self._suppress_ptag_stack[-1]:
            return '{}'.format(self.render_inner(token))
        template = format(self.render_inner(token))
        pre, suf, fg, bg, bold, ul, blink = unpack_style_fields(self.dix["paragraph"])
        return click.style(pre + template + suf, bg=bg, fg=fg, bold=bold, underline=ul, blink=blink)

    def render_block_code(self, token):
        template = '{}'
        strings = []
        pre, suf, fg, bg, bold, ul, blink = unpack_style_fields(self.dix["block_code"])
        for x in token.children[0].content.split("\n"):
            strings.append(click.style(pre + x + suf, fg=fg, bold=bold, bg=bg, underline=ul, blink=blink))
        inner = "\n".join(strings[:-1])
        return template.format(inner)

    def render_list(self, token):
        template = '{}'
        self._suppress_ptag_stack.append(not token.loose)
        inner = '\n'.join([self.render(child) for child in token.children])
        pre, suf, fg, bg, bold, ul, blink = unpack_style_fields(self.dix["list"])
        inner = pre + inner + suf
        self._suppress_ptag_stack.pop()
        return template.format(inner)

    def render_list_item(self, token):
        if len(token.children) == 0:
            return ''
        pre, suf, fg, bg, bold, ul, blink = unpack_style_fields(self.dix["item"])
        inner = pre + ''.join([self.render(child) for child in token.children]) + suf
        return '{}'.format(inner)

    @staticmethod
    def render_thematic_break(token):
        return '----------------------'

    @staticmethod
    def render_line_break(token):
        return '\n' if token.soft else '\n'

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        inner = '\n'.join([self.render(child) for child in token.children])
        return '{}\n'.format(inner) if inner else ''
