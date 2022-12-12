import uuid

import pytest

from pocket_storage import factories, models

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request):
    category = factories.ProductCategoryFactory.create()

    assert not models.Product.objects.exists()

    resp = web_request(
        'add_product',
        {
            'product_data': {
                'name': 'Краска',
                'SKU': 'SNI/01/136/0500',
                'barcode': '4600702084566',
                'category_id': str(category.id),
            },
        },
    )

    created_product = models.Product.objects.get()
    assert created_product.name == 'Краска'
    assert created_product.SKU == 'SNI/01/136/0500'
    assert created_product.barcode == '4600702084566'
    assert created_product.category_id == category.id

    assert resp.get('result') == {
        'id': str(created_product.id),
        'name': 'Краска',
        'SKU': 'SNI/01/136/0500',
        'barcode': '4600702084566',
        'category_id': str(category.id),
    }, resp.get('error')


def test_category_not_found__return_error(web_request):
    assert not models.ProductCategory.objects.exists()
    assert not models.Product.objects.exists()

    resp = web_request(
        'add_product',
        {
            'product_data': {
                'name': 'Краска',
                'SKU': 'SNI/01/136/0500',
                'barcode': '4600702084566',
                'category_id': str(uuid.uuid4()),
            },
        },
    )

    assert resp.get('error') == {
        'code': 3002,
        'message': 'Product category not found'
    }

    assert not models.Product.objects.exists()

def test_sku_already_exists__return_error(web_request):
    existing_product = factories.ProductFactory.create(
        SKU='SNI/03/213/1477',
        barcode='1800808073122',
    )

    resp = web_request(
        'add_product',
        {
            'product_data': {
                'name': 'Краска',
                'SKU': existing_product.SKU,
                'barcode': '4600702084566',
                'category_id': str(existing_product.category_id),
            }
        }
    )

    assert resp.get('error') == {
        'code': 4001,
        'message': 'Product already exists',
    }

    assert not models.Product.objects.exclude(id=existing_product.id).exists()


def test_barcode_already_exists__return_error(web_request):
    existing_product = factories.ProductFactory.create(
        SKU='SNI/03/213/1477',
        barcode='1800808073122',
    )

    resp = web_request(
        'add_product',
        {
            'product_data': {
                'name': 'Краска',
                'SKU': 'SNI/01/136/0500',
                'barcode': existing_product.barcode,
                'category_id': str(existing_product.category_id),
            }
        }
    )

    assert resp.get('error') == {
        'code': 4001,
        'message': 'Product already exists',
    }

    assert not models.Product.objects.exclude(id=existing_product.id).exists()
