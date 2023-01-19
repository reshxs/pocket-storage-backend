from django.core.management.base import BaseCommand
from pocket_storage import factories


class Command(BaseCommand):
    def handle(self, *args, **options):
        warehouse = factories.WarehouseFactory.create()

        root_category = factories.ProductCategoryFactory.create()
        leaf_categories = factories.ProductCategoryFactory.create_batch(
            3, parent_id=root_category.id
        )

        products = []
        for category in leaf_categories:
            product = factories.ProductFactory.create(category=category)
            products.append(product)

        for product in products:
            factories.StorageUnitFactory.create_batch(
                5, product=product, warehouse=warehouse
            )
