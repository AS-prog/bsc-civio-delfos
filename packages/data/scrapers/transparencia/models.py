from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PageSection:
    heading: str
    text: str


@dataclass
class AccordionItem:
    title: str
    content: str


@dataclass
class ExternalLink:
    url: str
    text: str


@dataclass
class PageData:
    url: str
    canonical: Optional[str] = None
    status_code: Optional[int] = None
    breadcrumb: list[str] = field(default_factory=list)
    title: Optional[str] = None
    updated_at: Optional[str] = None
    sections: list[PageSection] = field(default_factory=list)
    accordion_items: list[AccordionItem] = field(default_factory=list)
    external_links: list[ExternalLink] = field(default_factory=list)
    internal_links: list[str] = field(default_factory=list)
    crawled_at: Optional[str] = None
