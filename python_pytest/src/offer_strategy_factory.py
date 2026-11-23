"""Criação das estratégias de oferta (fábrica)."""

from model_objects import Offer, SpecialOfferType
from offer_strategies import (
    IOfferStrategy,
    NoOfferStrategy,
    PercentDiscountStrategy,
    QuantityForAmountStrategy,
    ThreeForTwoStrategy,
)


class OfferStrategyFactory:
    """Escolhe a estratégia de cálculo que corresponde ao tipo da oferta."""

    @staticmethod
    def create(offer: Offer) -> IOfferStrategy:
        if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
            return ThreeForTwoStrategy()
        if offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
            return PercentDiscountStrategy(offer.argument)
        if offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
            return QuantityForAmountStrategy(2, offer.argument)
        if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
            return QuantityForAmountStrategy(5, offer.argument)
        return NoOfferStrategy()
