from collections.abc import Callable

from model_objects import Offer, SpecialOfferType
from offer_strategies import (
    FiveForAmountStrategy,
    IOfferStrategy,
    PercentDiscountStrategy,
    ThreeForTwoStrategy,
    TwoForAmountStrategy,
)


class OfferStrategyFactory:
    _STRATEGY_BUILDERS: dict[SpecialOfferType, Callable[[float], IOfferStrategy]] = {
        SpecialOfferType.THREE_FOR_TWO: lambda argument: ThreeForTwoStrategy(),
        SpecialOfferType.TEN_PERCENT_DISCOUNT: lambda argument: PercentDiscountStrategy(argument),
        SpecialOfferType.TWO_FOR_AMOUNT: lambda argument: TwoForAmountStrategy(argument),
        SpecialOfferType.FIVE_FOR_AMOUNT: lambda argument: FiveForAmountStrategy(argument),
    }

    @staticmethod
    def create(offer: Offer) -> IOfferStrategy | None:
        build = OfferStrategyFactory._STRATEGY_BUILDERS.get(offer.offer_type)
        if build is None:
            return None
        return build(offer.argument)
