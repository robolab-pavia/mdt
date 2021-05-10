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
"""
mdt renderer for mistletoe.
"""

import click
from mistletoe.base_renderer import BaseRenderer

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
        template = click.style(self.dix[key]["prefix"] + "{}" + self.dix[key]["suffix"],
                               fg=self.dix[key]["color"], bold=self.dix[key]["bold"],
                               bg=self.dix[key]["background_color"], underline=self.dix[key]["underline"],
                               blink=self.dix[key]["blink"])
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
            template = click.style(self.dix["selected_link"]["prefix"] + '{inner}' + self.dix["selected_link"]["suffix"],
                                   fg=self.dix["selected_link"]["color"], bold=self.dix["selected_link"]["bold"],
                                   bg=self.dix["selected_link"]["background_color"],
                                   underline=self.dix["selected_link"]["underline"],
                                   blink=self.dix["selected_link"]["blink"]
                                   )
        else:
            template = click.style(self.dix["link"]["prefix"]+'{inner}'+self.dix["link"]["suffix"],
                                   fg=self.dix["link"]["color"], bold=self.dix["link"]["bold"],
                                   bg=self.dix["link"]["background_color"],
                                   underline=self.dix["link"]["underline"],
                                   blink=self.dix["link"]["blink"]
                                   )
        self.global_ref.update({inner: target})
        return template.format(target=target, inner=inner)

    def render_heading(self, token):
        key = "h" + str(token.level)
        pre = self.dix["heading"]["prefix"] if self.dix[key]["prefix"] == "" else self.dix[key]["prefix"]
        col = self.dix["heading"]["color"] if self.dix[key]["color"] == "" else self.dix[key]["color"]
        suf = self.dix["heading"]["suffix"] if self.dix[key]["suffix"] == "" else self.dix[key]["suffix"]
        bold = self.dix["heading"]["bold"] if self.dix[key]["bold"] == "" else self.dix[key]["bold"]
        back = self.dix["heading"]["background_color"] if self.dix[key]["background_color"] == "" else self.dix[key]["background_color"]
        under = self.dix["heading"]["underline"] if self.dix[key]["underline"] == "" else self.dix[key]["underline"]
        blink = self.dix["heading"]["blink"] if self.dix[key]["blink"] == "" else self.dix[key]["blink"]
        template = click.style(pre + "{inner}" + suf, bg=back, bold=bold, fg=col, underline=under, blink=blink)
        inner = self.render_inner(token)
        return template.format(inner=inner)

    def render_quote(self, token):
        elements = [""]
        self._suppress_ptag_stack.append(False)
        elements.extend([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        elements.append("")
        return click.style(self.dix["block_quote"]["prefix"]+''.join(elements)+self.dix["block_quote"]["suffix"],
                           fg=self.dix["block_quote"]["color"], bold=self.dix["block_quote"]["bold"],
                           bg=self.dix["block_quote"]["background_color"], underline=self.dix["block_quote"]["underline"],
                           blink=self.dix["block_quote"]["blink"]
                           )


    def render_paragraph(self, token):
        if self._suppress_ptag_stack[-1]:
            return '{}'.format(self.render_inner(token))
        template = format(self.render_inner(token))
        return click.style(self.dix["paragraph"]["prefix"]+template+self.dix["paragraph"]["suffix"], fg=self.dix["paragraph"]["color"], bold=self.dix["paragraph"]["bold"],
                           bg=self.dix["paragraph"]["background_color"], underline=self.dix["paragraph"]["underline"],
                           blink=self.dix["paragraph"]["blink"]
                           )

    def render_block_code(self, token):
        template = '{}'
        inner = "\n".join([click.style(self.dix["block_code"]["prefix"]+x+self.dix["block_code"]["suffix"], fg=self.dix["block_code"]["color"], bold=self.dix["block_code"]["bold"],
                           bg=self.dix["block_code"]["background_color"], underline=self.dix["block_code"]["underline"],
                           blink=self.dix["block_code"]["blink"]) if x != "" else x for x in token.children[0].content.split("\n")])
        return template.format(inner)

    def render_list(self, token):
        template = '{}'
        self._suppress_ptag_stack.append(not token.loose)
        inner = '\n'.join([self.render(child) for child in token.children])
        inner = self.dix["list"]["prefix"] + inner + self.dix["list"]["suffix"]
        self._suppress_ptag_stack.pop()
        return template.format(inner)

    def render_list_item(self, token):
        if len(token.children) == 0:
            return ''
        inner = self.dix["item"]["prefix"]+''.join([self.render(child) for child in token.children])+self.dix["item"]["suffix"]
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