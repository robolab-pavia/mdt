"""
mdt renderer for mistletoe.
"""

import re
import sys
import textwrap

import ansiwrap
import click
from itertools import chain
from urllib.parse import quote
from mistletoe.block_token import HTMLBlock
from mistletoe.span_token import HTMLSpan
from mistletoe.base_renderer import BaseRenderer
if sys.version_info < (3, 4):
    from mistletoe import _html as html
else:
    import html


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
        super().__init__(*chain((HTMLBlock, HTMLSpan), extras))
        # html.entities.html5 includes entitydefs not ending with ';',
        # CommonMark seems to hate them, so...
        self._stdlib_charref = html._charref
        _charref = re.compile(r'&(#[0-9]+;'
                              r'|#[xX][0-9a-fA-F]+;'
                              r'|[^\t\n\f <&#;]{1,32};)')
        html._charref = _charref

    def __exit__(self, *args):
        super().__exit__(*args)
        html._charref = self._stdlib_charref

    def render_to_plain(self, token):
        if hasattr(token, 'children'):
            inner = [self.render_to_plain(child) for child in token.children]
            return ''.join(inner)
        return self.escape_html(token.content)

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
        template =  click.style(self.dix["inline_code"]["prefix"] + "{}" + self.dix["inline_code"]["suffix"],
                               fg=self.dix["inline_code"]["color"], bold=self.dix["inline_code"]["bold"],
                               bg=self.dix["inline_code"]["background_color"], underline=self.dix["inline_code"]["underline"],
                               blink=self.dix["inline_code"]["blink"])
        inner = html.escape(token.children[0].content)
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
        target = self.escape_url(token.target)
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

    def render_auto_link(self, token):
        template = '"{target}">{inner}'
        if token.mailto:
            target = 'mailto:{}'.format(token.target)
        else:
            target = self.escape_url(token.target)
        inner = self.render_inner(token)
        return template.format(target=target, inner=inner)

    def render_escape_sequence(self, token):
        return self.render_inner(token)

    def render_raw_text(self, token):
        return self.escape_html(token.content)

    @staticmethod
    def render_html_span(token):
        return token.content

    def render_heading(self, token):
        if token.level == 1:
            template = click.style(self.dix["h1"]["prefix"]+'{inner}'+self.dix["h1"]["suffix"],
                                   fg=self.dix["h1"]["color"], bold=self.dix["h1"]["bold"],
                                   bg=self.dix["h1"]["background_color"], underline=self.dix["h1"]["underline"],
                                   blink=self.dix["h1"]["blink"]
                                   )
        elif token.level == 2:
            template = click.style(self.dix["h2"]["prefix"] + '{inner}' + self.dix["h2"]["suffix"],
                                   fg=self.dix["h2"]["color"], bold=self.dix["h2"]["bold"],
                                   bg=self.dix["h2"]["background_color"], underline=self.dix["h2"]["underline"],
                                   blink=self.dix["h2"]["blink"]
                                   )
        elif token.level == 3:
            template = click.style(self.dix["h3"]["prefix"] + '{inner}' + self.dix["h3"]["suffix"],
                                   fg=self.dix["h3"]["color"], bold=self.dix["h3"]["bold"],
                                   bg=self.dix["h3"]["background_color"], underline=self.dix["h3"]["underline"],
                                   blink=self.dix["h3"]["blink"]
                                   )
        elif token.level == 4:
            template = click.style(self.dix["h4"]["prefix"] + '{inner}' + self.dix["h4"]["suffix"],
                                   fg=self.dix["h4"]["color"], bold=self.dix["h4"]["bold"],
                                   bg=self.dix["h4"]["background_color"], underline=self.dix["h4"]["underline"],
                                   blink=self.dix["h4"]["blink"]
                                   )
        elif token.level == 5:
            template = click.style(self.dix["h5"]["prefix"] + '{inner}' + self.dix["h5"]["suffix"],
                                   fg=self.dix["h5"]["color"], bold=self.dix["h5"]["bold"],
                                   bg=self.dix["h5"]["background_color"], underline=self.dix["h5"]["underline"],
                                   blink=self.dix["h5"]["blink"]
                                   )
        elif token.level == 6:
            template = click.style(self.dix["h6"]["prefix"] + '{inner}' + self.dix["h6"]["suffix"],
                                   fg=self.dix["h6"]["color"], bold=self.dix["h6"]["bold"],
                                   bg=self.dix["h6"]["background_color"], underline=self.dix["h6"]["underline"],
                                   blink=self.dix["h6"]["blink"]
                                   )
        inner = self.render_inner(token)
        return template.format(level=token.level, inner=inner)

    def render_quote(self, token):
        elements = [""]
        self._suppress_ptag_stack.append(False)
        elements.extend([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        elements.append("")
        return click.style(self.dix["block_quote"]["prefix"]+''.join(elements)+self.dix["block_quote"]["suffix"],
                           fg=self.dix["h6"]["color"], bold=self.dix["h6"]["bold"],
                           bg=self.dix["h6"]["background_color"], underline=self.dix["h6"]["underline"],
                           blink=self.dix["h6"]["blink"]
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
        template = '{attr}>{inner}'
        if token.language:
            attr = ' class="{}"'.format('language-{}'.format(self.escape_html(token.language)))
        else:
            attr = ''
        inner = html.escape(token.children[0].content)
        return template.format(attr=attr, inner=inner)

    def render_list(self, token):
        template = '{}'
        self._suppress_ptag_stack.append(not token.loose)
        inner = ''.join([self.render(child) for child in token.children])
        self._suppress_ptag_stack.pop()
        return template.format(inner)

    def render_list_item(self, token):
        if len(token.children) == 0:
            return ''
        inner = self.dix["item"]["prefix"]+''.join([self.render(child) for child in token.children])+self.dix["item"]["suffix"]
        inner_template = self.dix["item"]["prefix"]+"{}"+self.dix["item"]["suffix"]
        return '{}'.format(inner)

    @staticmethod
    def render_thematic_break(token):
        return '<hr />'

    @staticmethod
    def render_line_break(token):
        return '\n' if token.soft else '<br />\n'

    @staticmethod
    def render_html_block(token):
        return token.content

    def render_document(self, token):
        self.footnotes.update(token.footnotes)
        inner = '\n'.join([self.render(child) for child in token.children])
        return '{}\n'.format(inner) if inner else ''

    @staticmethod
    def escape_html(raw):
        return html.escape(html.unescape(raw)).replace('&#x27;', "'")

    @staticmethod
    def escape_url(raw):
        """
        Escape urls to prevent code injection craziness. (Hopefully.)
        """
        return html.escape(quote(html.unescape(raw), safe='/#:()*?=%@+,&'))
