"""
mdt renderer for mistletoe.
"""

import sys
import click
from itertools import chain
from mistletoe.block_token import HTMLBlock
from mistletoe.span_token import HTMLSpan
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

    def render_strong(self, token):
        template = click.style(self.dix["strong"]["prefix"]+"{}"+self.dix["strong"]["suffix"],
                               fg=self.dix["strong"]["color"], bold=self.dix["strong"]["bold"],
                               bg=self.dix["strong"]["background_color"], underline=self.dix["strong"]["underline"],
                               blink=self.dix["strong"]["blink"])
        return template.format(self.render_inner(token))

    def render_emphasis(self, token):
        template = click.style(self.dix["emph"]["prefix"] + "{}" + self.dix["emph"]["suffix"],
                               fg=self.dix["emph"]["color"], bold=self.dix["emph"]["bold"],
                               bg=self.dix["emph"]["background_color"], underline=self.dix["emph"]["underline"],
                               blink=self.dix["emph"]["blink"])
        return template.format(self.render_inner(token))

    def render_inline_code(self, token):
        template = click.style(self.dix["inline_code"]["prefix"] + "{}" + self.dix["inline_code"]["suffix"],
                               fg=self.dix["inline_code"]["color"], bold=self.dix["inline_code"]["bold"],
                               bg=self.dix["inline_code"]["background_color"], underline=self.dix["inline_code"]["underline"],
                               blink=self.dix["inline_code"]["blink"])
        inner = token.children[0].content
        return template.format(inner)

    def render_strikethrough(self, token):
        template = click.style(self.dix["strikethrough"]["prefix"] + "{}" + self.dix["strikethrough"]["suffix"],
                               fg=self.dix["strikethrough"]["color"], bold=self.dix["strikethrough"]["bold"],
                               bg=self.dix["strikethrough"]["background_color"],
                               underline=self.dix["strikethrough"]["underline"],
                               blink=self.dix["strikethrough"]["blink"]
                               )
        return template.format(self.render_inner(token))

    def render_link(self, token):
        target = token.target
        inner = self.render_inner(token)
        if inner.startswith('\007'):
            inner = inner.replace('\007', '')
            template = click.style(self.dix["choosen_link"]["prefix"] + '{inner}' + self.dix["choosen_link"]["suffix"],
                                   fg=self.dix["choosen_link"]["color"], bold=self.dix["choosen_link"]["bold"],
                                   bg=self.dix["choosen_link"]["background_color"],
                                   underline=self.dix["choosen_link"]["underline"],
                                   blink=self.dix["choosen_link"]["blink"]
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
        self._suppress_ptag_stack.pop()
        return template.format(inner)

    def render_list_item(self, token):
        if len(token.children) == 0:
            return ''
        inner = self.dix["item"]["prefix"]+''.join([self.render(child) for child in token.children])+self.dix["item"]["suffix"]
        return '{}'.format(inner)

    @staticmethod
    def render_thematic_break(token):
        return '---'

    @staticmethod
    def render_line_break(token):
        return '\n' if token.soft else '\n'

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        inner = '\n'.join([self.render(child) for child in token.children])
        return '{}\n'.format(inner) if inner else ''











