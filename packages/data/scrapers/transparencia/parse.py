import re
from typing import Optional
from urllib.parse import urljoin

from selectolax.parser import HTMLParser, Node

from scrapers.transparencia.models import (
    AccordionItem,
    ExternalLink,
    PageData,
    PageSection,
)

LANG_PREFIXES = re.compile(r"^\/(ca|eu|gl|va|en)\/")
FRAGMENT = re.compile(r"#.*$")
PUBLICIDAD_ACTIVA = re.compile(r"^/publicidad-activa")
DAM_CONTENT = re.compile(r"/content/dam/")
BOE = re.compile(r"https?://(www\.)?boe\.es")

def _matches(pattern: re.Pattern, value: str) -> bool:
    return bool(pattern.search(value))

UPDATED_RE = re.compile(
    r"Actualizado a (\d{1,2}/\d{1,2}/\d{4})",
    re.IGNORECASE,
)


def _is_internal(href: str) -> bool:
    return bool(PUBLICIDAD_ACTIVA.match(href))


def _is_excluded_lang(href: str) -> bool:
    return bool(LANG_PREFIXES.match(href))


def _normalise(path: str) -> str:
    return FRAGMENT.sub("", path).rstrip("/")


def _text(node: Optional[Node]) -> str:
    if node is None:
        return ""
    return node.text(deep=True, separator=" ").strip()


def _has_class(node: Node, class_name: str) -> bool:
    return class_name in node.attributes.get("class", "").split()


def _children_text(node: Node, selector: str) -> list[str]:
    return [
        _text(n)
        for n in node.css(selector)
        if _text(n)
    ]


class TransparenciaParser:

    def parse(self, url: str, html: str) -> PageData:
        tree = HTMLParser(html)
        data = PageData(url=url)

        data.canonical = self._canonical(tree)
        data.status_code = 200
        data.breadcrumb = self._breadcrumb(tree)
        data.title = self._title(tree)
        data.updated_at = self._updated_at(tree)
        data.sections = self._sections(tree)
        data.accordion_items = self._accordion_items(tree)
        data.external_links = self._external_links(tree, url)
        data.internal_links = self._internal_links(tree)

        return data

    def _canonical(self, tree: HTMLParser) -> Optional[str]:
        link = tree.css_first('link[rel="canonical"]')
        if link:
            return link.attributes.get("href")
        return None

    def _breadcrumb(self, tree: HTMLParser) -> list[str]:
        crumbs = []
        for li in tree.css("nav.cmp-breadcrumb li, .cmp-breadcrumb li"):
            a = li.css_first("a")
            if a:
                t = _text(a)
                if t:
                    crumbs.append(t)
            else:
                t = _text(li)
                if t and t != li.text().strip():
                    crumbs.append(t)
        return crumbs

    def _title(self, tree: HTMLParser) -> Optional[str]:
        h1 = tree.css_first("h1.cmp-title__text")
        if h1:
            return _text(h1)
        h1 = tree.css_first("h1")
        if h1:
            return _text(h1)
        return None

    def _updated_at(self, tree: HTMLParser) -> Optional[str]:
        for el in tree.css("main, div.cmp-text"):
            text = _text(el)
            m = UPDATED_RE.search(text)
            if m:
                return m.group(1)
        return None

    def _sections(self, tree: HTMLParser) -> list[PageSection]:
        # In the Transparencia AEM markup, a heading lives inside its own
        # ``div.cmp-title`` wrapper and the body text lives in separate
        # ``div.cmp-text`` containers further down the document — they are NOT
        # direct siblings of the heading. So we walk headings and text blocks
        # in document order and attach each text block to the last open heading.
        scope = tree.css_first("main") or tree.body or tree.root
        headings: list[str] = []
        buffers: list[list[str]] = []
        current_parts: Optional[list[str]] = None
        for node in scope.traverse():
            is_heading = (
                node.tag in ("h2", "h3")
                and _has_class(node, "cmp-title__text")
            )
            is_text = node.tag == "div" and _has_class(node, "cmp-text")
            if is_heading:
                title = _text(node)
                if not title:
                    continue
                current_parts = []
                headings.append(title)
                buffers.append(current_parts)
            elif is_text:  # div.cmp-text — body content
                if current_parts is None:
                    continue
                text = _text(node)
                if text:
                    current_parts.append(text)
        return [
            PageSection(heading=heading, text="\n".join(parts))
            for heading, parts in zip(headings, buffers)
        ]

    def _accordion_items(self, tree: HTMLParser) -> list[AccordionItem]:
        items = []
        for item in tree.css(".cmp-accordion__item"):
            title_el = item.css_first(".cmp-accordion__title, .accordion-title")
            panel = item.css_first(".cmp-accordion__panel, .accordion-panel")
            title = _text(title_el) if title_el else ""
            content = _text(panel) if panel else ""
            if title or content:
                items.append(AccordionItem(title=title, content=content))
        return items

    def _external_links(self, tree: HTMLParser, base: str) -> list[ExternalLink]:
        links = []
        seen = set()
        for a in tree.css("a[href]"):
            href = a.attributes.get("href", "").strip()
            text = _text(a)
            if not href or not text:
                continue
            resolved = urljoin(base, href)
            if _matches(BOE, resolved) or _matches(DAM_CONTENT, resolved):
                if resolved not in seen:
                    seen.add(resolved)
                    links.append(ExternalLink(url=resolved, text=text))
            if a.attributes.get("target") == "_blank" and not _is_internal(
                href
            ):
                if resolved not in seen:
                    seen.add(resolved)
                    links.append(ExternalLink(url=resolved, text=text))
        return links

    def _internal_links(self, tree: HTMLParser) -> list[str]:
        links = []
        seen = set()
        for a in tree.css("a[href]"):
            href = a.attributes.get("href", "").strip()
            if not href:
                continue
            normalised = _normalise(href)
            if (
                _is_internal(normalised)
                and not _is_excluded_lang(normalised)
                and normalised not in seen
            ):
                seen.add(normalised)
                links.append(normalised)
        return links

    def extract_links(self, html: str) -> list[str]:
        tree = HTMLParser(html)
        return self._internal_links(tree)
