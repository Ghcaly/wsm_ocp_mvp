from decimal import Decimal
from .space_size import SpaceSize 


class CalculatorConstants:
    MINIMUN_QUANTITY_TO_JOIN_DISPOSABLES = 7
    MAXIMUM_QUANTITY_DIFFERENT_PRODUCTS_ON_PALLET = 16
    MINIMUM_OCCUPATION_TO_SWITCH_DISPOSABLE_MOUNTED_SPACES = 7

    MAXIMUM_DISTRIBUTION_PER_SIDE = 60
    MINIMUM_DISTRIBUTION_PER_SIDE = 40
    BEST_DISTRIBUTION_PER_SIDE = 50
    MINIMUM_MOUNTED_SPACES_TO_BALANCE = 2

    MAXIMUM_FRACTIONAL_VALUE_TO_ROUND = Decimal("0.05")
    MINIMUM_FRACTIONAL_VALUE_TO_ROUND = Decimal("0.95")
    BOXES_QUANTITY_IN_PALLET = int(SpaceSize.Size42)

    NUMBER_OF_MAX_RETRIES = 20

    SAFE_SIDE_RULE_MIN_TRUCK_BAYS = 2
    SAFE_SIDE_RULE_MAX_TRUCK_BAYS = 12
    MAXIMUM_VALID_DISTRIBUTION_PER_SIDE = Decimal("0.7")
    MINIMUM_VALID_DISTRIBUTION_PER_SIDE = Decimal("0.3")  # 1 - 0.7

    ComparatorItemWidth = Decimal("35.01")
    ComparatorItemLenght = Decimal("51.20")
    ComparatorItemBallastQuantity = 7
    ComparatorItemTotalAreaOccupiedByUnit = ComparatorItemWidth * ComparatorItemLenght
    ComparatorItemTotalAreaOccupiedByBallast = ComparatorItemTotalAreaOccupiedByUnit * ComparatorItemBallastQuantity

    MAX_GROSS_WEIGHT = Decimal("25")