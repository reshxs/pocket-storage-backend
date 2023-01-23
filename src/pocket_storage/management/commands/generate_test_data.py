from django.core.management.base import BaseCommand
from pocket_storage import factories


class Command(BaseCommand):
    def handle(self, *args, **options):
        warehouse = factories.WarehouseFactory.create(name='Склад: Коммунаров 47')

        root_category = factories.ProductCategoryFactory.create(name='Чистовой ремонт')

        factories.ProductCategoryFactory.create(
            name='Штукатурка',
            parent_id=root_category.id,
        )
        factories.ProductCategoryFactory.create(
            name='Обои',
            parent_id=root_category.id,
        )

        category = factories.ProductCategoryFactory.create(
            name='Краска',
            parent_id=root_category.id
        )

        products = [
            factories.ProductFactory.create(
                name='Краска акриловая красная',
                SKU='SNI/01/136/0500',
                barcode='4600702084566',
                category=category,
            ),
            factories.ProductFactory.create(
                name='Краска акриловая синяя',
                SKU='SNI/01/136/0512',
                barcode='4600702084321',
                category=category,
            ),
            factories.ProductFactory.create(
                name='Краска акриловая розовая',
                SKU='SNI/01/136/0547',
                barcode='4600702081234',
                category=category,
            ),
        ]

        for index, product in enumerate(products, 1):
            for i in range(1+index, 5+index):
                factories.StorageUnitFactory.create(
                    product=product, warehouse=warehouse, ext_id='F' + f'{index*i}'*index
                )
