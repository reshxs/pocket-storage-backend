import uuid

import pytest

from pocket_storage import models, factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_add_category_without_parent__ok(web_request):
    assert not models.ProductCategory.objects.exists()

    resp = web_request(
        "add_product_category",
        {
            "name": "Краска",
        },
    )

    created_category = models.ProductCategory.objects.get()
    assert created_category.name == "Краска"
    assert created_category.parent_id is None

    assert resp.get("result") == {
        "id": str(created_category.id),
        "name": "Краска",
        "parent_id": None,
    }, resp.get("error")


def test_add_category_without_parent__already_exists(web_request):
    existing_category = factories.ProductCategoryFactory.create()

    resp = web_request(
        "add_product_category",
        {
            "name": existing_category.name,
        },
    )

    assert resp.get("error") == {
        "code": 3001,
        "message": "Product category already exists",
    }

    assert not models.ProductCategory.objects.exclude(id=existing_category.id).exists()


def test_add_category_with_parent__ok(web_request):
    parent_category = factories.ProductCategoryFactory.create()

    assert not models.ProductCategory.objects.exclude(id=parent_category.id).exists()

    resp = web_request(
        "add_product_category",
        {"name": "Новая категория", "parent_id": str(parent_category.id)},
    )

    created_category = models.ProductCategory.objects.exclude(
        id=parent_category.id
    ).get()
    assert created_category.name == "Новая категория"
    assert created_category.parent_id == parent_category.id

    assert resp.get("result") == {
        "id": str(created_category.id),
        "name": "Новая категория",
        "parent_id": str(parent_category.id),
    }, resp.get("error")


def test_add_category_with_parent__already_exists(web_request):
    parent_category = factories.ProductCategoryFactory.create()
    existing_category = factories.ProductCategoryFactory.create(
        parent_id=parent_category.id
    )

    resp = web_request(
        "add_product_category",
        {"name": existing_category.name, "parent_id": str(parent_category.id)},
    )

    assert resp.get("error") == {
        "code": 3001,
        "message": "Product category already exists",
    }

    assert not models.ProductCategory.objects.exclude(
        id__in=[parent_category.id, existing_category.id]
    ).exists()


def test_add_category_with_parent__same_name_in_other_scope__ok(web_request):
    parent_category = factories.ProductCategoryFactory.create()
    other_parent_category = factories.ProductCategoryFactory.create()
    existing_category = factories.ProductCategoryFactory.create(
        parent_id=other_parent_category.id
    )

    assert not models.ProductCategory.objects.exclude(
        id__in=[parent_category.id, existing_category.id, other_parent_category.id]
    ).exists()

    resp = web_request(
        "add_product_category",
        {"name": existing_category.name, "parent_id": str(parent_category.id)},
    )

    created_category = models.ProductCategory.objects.exclude(
        id__in=[parent_category.id, existing_category.id, other_parent_category.id]
    ).get()
    assert created_category.name == existing_category.name
    assert created_category.parent_id == parent_category.id

    assert resp.get("result") == {
        "id": str(created_category.id),
        "name": existing_category.name,
        "parent_id": str(parent_category.id),
    }, resp.get("error")


def test_parent_does_not_exists(web_request):
    assert not models.ProductCategory.objects.exists()

    resp = web_request(
        "add_product_category",
        {"name": "Краска", "parent_id": str(uuid.uuid4())},
    )

    assert resp.get("error") == {"code": 3002, "message": "Product category not found"}
