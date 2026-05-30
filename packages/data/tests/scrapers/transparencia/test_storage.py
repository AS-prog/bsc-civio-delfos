import polars as pl

from scrapers.transparencia.models import AccordionItem, PageData
from scrapers.transparencia.storage import TransparenciaStorage


def test_exports_accordion_items_to_parquet(tmp_path):
    warehouse_dir = tmp_path / "warehouse"
    storage = TransparenciaStorage(
        raw_dir=tmp_path / "raw",
        warehouse_dir=warehouse_dir,
    )
    storage.save_page(
        PageData(
            url="https://transparencia.gob.es/example",
            accordion_items=[
                AccordionItem(title="RPT", content="Contenido del acordeon"),
            ],
        )
    )

    storage.flush()

    df = pl.read_parquet(str(warehouse_dir / "transparencia_accordion.parquet"))
    assert df.to_dicts() == [
        {
            "url": "https://transparencia.gob.es/example",
            "ord": 1,
            "title": "RPT",
            "content": "Contenido del acordeon",
        }
    ]
