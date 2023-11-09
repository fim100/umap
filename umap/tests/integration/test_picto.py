from pathlib import Path

import pytest
from playwright.sync_api import expect
from django.core.files.base import ContentFile

from umap.models import Map, Pictogram

from ..base import DataLayerFactory

pytestmark = pytest.mark.django_db


DATALAYER_DATA = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [13.68896484375, 48.55297816440071],
            },
            "properties": {"_umap_options": {"color": "DarkCyan"}, "name": "Here"},
        }
    ],
    "_umap_options": {"displayOnLoad": True, "name": "FooBarFoo"},
}
FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def pictos():
    path = FIXTURES / "star.svg"
    Pictogram(name="star", pictogram=ContentFile(path.read_text(), path.name)).save()
    path = FIXTURES / "circle.svg"
    Pictogram(name="circle", pictogram=ContentFile(path.read_text(), path.name)).save()


def test_can_change_picto_at_map_level(map, live_server, page, pictos):
    # Faster than doing a login
    map.edit_status = Map.ANONYMOUS
    map.save()
    DataLayerFactory(map=map, data=DATALAYER_DATA)
    page.goto(f"{live_server.url}{map.get_absolute_url()}?edit")
    marker = page.locator(".umap-div-icon img")
    expect(marker).to_have_count(1)
    # Should have default img
    expect(marker).to_have_attribute("src", "/static/umap/img/marker.png")
    edit_settings = page.get_by_title("Edit map settings")
    expect(edit_settings).to_be_visible()
    edit_settings.click()
    shape_settings = page.get_by_text("Default shape properties")
    expect(shape_settings).to_be_visible()
    shape_settings.click()
    define = page.locator(".umap-field-iconUrl .define")
    undefine = page.locator(".umap-field-iconUrl .undefine")
    expect(define).to_be_visible()
    expect(undefine).to_be_hidden()
    define.click()
    symbols = page.locator(".umap-pictogram-choice")
    expect(symbols).to_have_count(2)
    search = page.locator(".umap-pictogram-list input")
    search.type("star")
    expect(symbols).to_have_count(1)
    symbols.click()
    expect(marker).to_have_attribute("src", "/uploads/pictogram/star.svg")
    undefine.click()
    expect(marker).to_have_attribute("src", "/static/umap/img/marker.png")
