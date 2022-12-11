import uuid

import pytest
from dirty_equals import IsPartialDict
from django.forms import model_to_dict

from pocket_storage import factories, models

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_ok(web_request):
    category = factories.ProductCategoryFactory.create(name="old_name")

    resp = web_request(
        "rename_product_category",
        {
            "id": str(category.id),
            "new_name": "new_name",
        },
    )

    assert resp.get("result") == IsPartialDict(
        {
            "id": str(category.id),
            "name": "new_name",
        },
    ), resp.get("error")

    category.refresh_from_db()
    assert category.name == "new_name"


def test_category_not_found__return_error(web_request):
    assert not models.ProductCategory.objects.exists()

    resp = web_request(
        "rename_product_category",
        {
            "id": str(uuid.uuid4()),
            "new_name": "new_name",
        },
    )

    assert resp.get("error") == {
        "code": 3002,
        "message": "Product category not found",
    }


def test_product_category_with_same_name__return_error(web_request):
    category = factories.ProductCategoryFactory.create()
    other_category = factories.ProductCategoryFactory.create()

    resp = web_request(
        "rename_product_category",
        {
            "id": str(category.id),
            "new_name": other_category.name,
        },
    )

    assert resp.get("error") == {
        "code": 3001,
        "message": "Product category already exists",
    }

    old_category = model_to_dict(category)
    category.refresh_from_db()
    actual_category = model_to_dict(category)
    assert old_category == actual_category
