import pytest
from dirty_equals import IsListOrTuple
from pocket_storage import factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_empty_list(web_request):
    resp = web_request("get_product_categories")
    assert resp.get("result") == [], resp.get("error")


def test_ok(web_request):
    parent_category = factories.ProductCategoryFactory.create()
    child_categories = factories.ProductCategoryFactory.create_batch(
        3, parent_id=parent_category.id
    )

    resp = web_request("get_product_categories")

    assert resp.get("result") == IsListOrTuple(
        *[
            {
                "id": str(category.id),
                "name": category.name,
                "parent_id": str(category.parent_id) if category.parent_id else None,
            }
            for category in [parent_category, *child_categories]
        ],
        check_order=False,
    ), resp.get("error")


def test_filter_by_parent_category(web_request):
    parent_category = factories.ProductCategoryFactory.create()
    expected_category = factories.ProductCategoryFactory.create(
        parent_id=parent_category.id
    )

    other_parent_category = factories.ProductCategoryFactory.create()
    factories.ProductCategoryFactory.create(
        parent_id=other_parent_category.id
    )  # unexpected_category

    resp = web_request(
        "get_product_categories",
        {
            "parent_id": str(parent_category.id),
        },
    )

    assert resp.get("result") == [
        {
            "id": str(expected_category.id),
            "name": expected_category.name,
            "parent_id": str(expected_category.parent_id),
        }
    ], resp.get("error")
