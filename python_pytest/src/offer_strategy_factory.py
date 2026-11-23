"""Criação das estratégias de oferta (fábrica)."""

from model_objects import Offer, SpecialOfferType
from offer_strategies import (
    IOfferStrategy,
    NoOfferStrategy,
    PercentDiscountStrategy,
    QuantityForAmountStrategy,
    ThreeForTwoStrategy,
)

# Tamanho do grupo de cada oferta do tipo "N unidades por um valor fechado".
GROUP_SIZE_BY_OFFER_TYPE = {
    SpecialOfferType.TWO_FOR_AMOUNT: 2,
    SpecialOfferType.FIVE_FOR_AMOUNT: 5,
}


class OfferStrategyFactory:
    """Escolhe a estratégia de cálculo que corresponde ao tipo da oferta."""

    @staticmethod
    def create(offer: Offer) -> IOfferStrategy:
        if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
            return ThreeForTwoStrategy()
        if offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
            return PercentDiscountStrategy(offer.argument)
        if offer.offer_type in GROUP_SIZE_BY_OFFER_TYPE:
            group_size = GROUP_SIZE_BY_OFFER_TYPE[offer.offer_type]
            return QuantityForAmountStrategy(group_size, offer.argument)
        return NoOfferStrategy()
