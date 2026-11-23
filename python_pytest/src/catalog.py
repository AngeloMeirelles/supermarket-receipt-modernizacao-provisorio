from model_objects import Product

DATABASE_ACCESS_MESSAGE = "cannot be called from a unit test - it accesses the database"


class SupermarketCatalog:
    # O caixa (Teller.product_with_name) consulta os produtos pelo nome.
    products: dict[str, Product]

    # A exceção genérica foi mantida para não alterar o comportamento do legado.
    def add_product(self, product: Product, price: float) -> None:
        raise Exception(DATABASE_ACCESS_MESSAGE)

    def unit_price(self, product: Product) -> float:
        raise Exception(DATABASE_ACCESS_MESSAGE)
