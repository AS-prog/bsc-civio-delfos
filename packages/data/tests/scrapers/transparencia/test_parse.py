from pathlib import Path

from scrapers.transparencia.models import PageData
from scrapers.transparencia.parse import TransparenciaParser

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class TestCanonical:

    def test_extracts_canonical_link(self):
        html = '<html><head><link rel="canonical" href="https://transparencia.gob.es/test"></head></html>'
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert data.canonical == "https://transparencia.gob.es/test"

    def test_none_when_missing(self):
        html = "<html><head></head><body><p>no canonical</p></body></html>"
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert data.canonical is None


class TestBreadcrumb:

    def test_extracts_breadcrumb_links(self):
        html = """
        <html><body>
        <nav class="cmp-breadcrumb">
            <li><a href="/">Inicio</a></li>
            <li><a href="/publicidad-activa">Publicidad Activa</a></li>
            <li>Funciones</li>
        </nav>
        </body></html>
        """
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert "Inicio" in data.breadcrumb
        assert "Publicidad Activa" in data.breadcrumb

    def test_empty_when_no_breadcrumb(self):
        html = "<html><body><p>no breadcrumb</p></body></html>"
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert data.breadcrumb == []


class TestTitle:

    def test_extracts_h1_title(self):
        html = '<html><body><h1 class="cmp-title__text">Presidencia del Gobierno</h1></body></html>'
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert data.title == "Presidencia del Gobierno"

    def test_fallback_to_plain_h1(self):
        html = "<html><body><h1>Ministerio de Hacienda</h1></body></html>"
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert data.title == "Ministerio de Hacienda"

    def test_none_when_no_h1(self):
        html = "<html><body><p>no title</p></body></html>"
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert data.title is None


class TestUpdatedAt:

    def test_extracts_update_date(self):
        html = "<html><body><main><p>Actualizado a 15/03/2025</p></main></body></html>"
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert data.updated_at == "15/03/2025"

    def test_none_when_no_date(self):
        html = "<html><body><main><p>sin fecha</p></main></body></html>"
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert data.updated_at is None


class TestInternalLinks:

    def test_extracts_internal_links(self):
        html = """
        <html><body>
        <a href="/publicidad-activa/por-materias">Materias</a>
        <a href="/publicidad-activa/por-materias/organizacion-empleo">Org</a>
        <a href="https://www.boe.es">BOE</a>
        <a href="/ca/publicidad-activa">Català</a>
        </body></html>
        """
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert "/publicidad-activa/por-materias" in data.internal_links
        assert "/publicidad-activa/por-materias/organizacion-empleo" in data.internal_links
        assert "/ca/publicidad-activa" not in data.internal_links

    def test_excludes_fragments(self):
        html = """
        <html><body>
        <a href="/publicidad-activa#section1">Con fragment</a>
        <a href="/publicidad-activa">Sin fragment</a>
        </body></html>
        """
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert "/publicidad-activa" in data.internal_links
        assert len(data.internal_links) == 1


class TestSections:

    def test_extracts_h2_sections(self):
        html = """
        <html><body>
        <h2 class="cmp-title__text">Organigrama</h2>
        <div class="cmp-text"><p>Descripción del organigrama</p></div>
        <h2 class="cmp-title__text">Funciones</h2>
        <div class="cmp-text"><p>Listado de funciones</p></div>
        </body></html>
        """
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        headings = [s.heading for s in data.sections]
        assert "Organigrama" in headings
        assert "Funciones" in headings

    def test_empty_when_no_h2(self):
        html = "<html><body><p>no sections</p></body></html>"
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert data.sections == []

    def test_captures_body_text_in_aem_layout(self):
        # Real AEM markup: the heading sits inside its own div.cmp-title
        # wrapper and the body text lives in separate div.cmp-text containers
        # that are NOT direct siblings of the heading.
        html = """
        <html><body><main>
        <div class="vertical-menu navigation">
            <div class="cmp-title"><div class="cmp-title__text">Publicidad Activa</div></div>
        </div>
        <div class="cmp-container">
            <div class="cmp-title"><h2 class="cmp-title__text">Compatibilidad de empleados públicos</h2></div>
        </div>
        <div class="cmp-container">
            <div class="cmp-text"><p>Fuente de los datos</p></div>
        </div>
        <div class="cmp-container">
            <div class="cmp-text"><p>Periodicidad: Trimestral</p></div>
        </div>
        </main></body></html>
        """
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert len(data.sections) == 1
        section = data.sections[0]
        assert section.heading == "Compatibilidad de empleados públicos"
        assert "Fuente de los datos" in section.text
        assert "Periodicidad: Trimestral" in section.text
        # the side-menu title is a div (not a heading) → must not be a section
        assert all(s.heading != "Publicidad Activa" for s in data.sections)

    def test_assigns_text_to_correct_heading(self):
        html = """
        <html><body><main>
        <div class="cmp-title"><h2 class="cmp-title__text">Funciones</h2></div>
        <div class="cmp-text"><p>Texto de funciones</p></div>
        <div class="cmp-title"><h2 class="cmp-title__text">Normativa</h2></div>
        <div class="cmp-text"><p>Texto de normativa</p></div>
        </main></body></html>
        """
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        by_heading = {s.heading: s.text for s in data.sections}
        assert by_heading["Funciones"] == "Texto de funciones"
        assert by_heading["Normativa"] == "Texto de normativa"


class TestAccordionItems:

    def test_extracts_accordion_items(self):
        html = """
        <html><body>
        <div class="cmp-accordion__item">
            <span class="cmp-accordion__title">Sección 1</span>
            <div class="cmp-accordion__panel">Contenido 1</div>
        </div>
        <div class="cmp-accordion__item">
            <span class="cmp-accordion__title">Sección 2</span>
            <div class="cmp-accordion__panel">Contenido 2</div>
        </div>
        </body></html>
        """
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        titles = [a.title for a in data.accordion_items]
        assert "Sección 1" in titles
        assert "Sección 2" in titles

    def test_empty_when_no_accordion(self):
        html = "<html><body><p>no accordion</p></body></html>"
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert data.accordion_items == []


class TestExternalLinks:

    def test_extracts_boe_links(self):
        html = """
        <html><body>
        <a href="https://www.boe.es/buscar/act.php?id=BOE-A-2024-1234">BOE</a>
        </body></html>
        """
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert any("boe.es" in l.url for l in data.external_links)

    def test_extracts_dam_links(self):
        html = """
        <html><body>
        <a href="/content/dam/transparencia/doc.pdf">PDF</a>
        </body></html>
        """
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert any("/content/dam/" in l.url for l in data.external_links)

    def test_empty_when_no_external_links(self):
        html = "<html><body><p>no links</p></body></html>"
        parser = TransparenciaParser()
        data = parser.parse("https://transparencia.gob.es/test", html)
        assert data.external_links == []
