"""
Python port of C# ItemExtensions static methods.
These methods filter and order collections of items.
"""
from typing import List, Iterable
from .item import Item


def is_chopp(items: Iterable[Item]) -> List[Item]:
    """Filter items where product is Chopp"""
    return [x for x in items if x.IsChopp()]


def not_chopp(items: Iterable[Item]) -> List[Item]:
    """Filter items where product is NOT Chopp"""
    return [x for x in items if x.NotChopp()]


def is_isotonic_water(items: Iterable[Item]) -> List[Item]:
    """Filter items where product is IsotonicWater"""
    return [x for x in items if x.IsIsotonicWater()]


def not_isotonic_water(items: Iterable[Item]) -> List[Item]:
    """Filter items where product is NOT IsotonicWater"""
    return [x for x in items if x.NotIsotonicWater()]


def is_returnable(items: Iterable[Item]) -> List[Item]:
    """Filter items where product is Returnable"""
    return [x for x in items if x.IsReturnable()]


def is_package(items: Iterable[Item]) -> List[Item]:
    """Filter items where product is Package"""
    return [x for x in items if x.IsPackage()]


def is_box_template(items: Iterable[Item]) -> List[Item]:
    """Filter items where product is BoxTemplate"""
    return [x for x in items if x.IsBoxTemplate()]


def not_marketplace(items: Iterable[Item]) -> List[Item]:
    """Filter items where product is NOT marketplace (not Package and not BoxTemplate)"""
    return [x for x in items if x.NotMarketplace()]


def with_configuration(items: Iterable[Item], include_top_of_pallet: bool) -> List[Item]:
    """
    C#: items.Where(x => x.WithConfiguration(includeTopOfPallet))
    """
    return [x for x in items if x.WithConfiguration(include_top_of_pallet)]


def with_layer_code(items: Iterable[Item]) -> List[Item]:
    """Filter items where product.LayerCode > 0"""
    return [x for x in items if x.WithLayerCode()]


def without_layer_code(items: Iterable[Item]) -> List[Item]:
    """Filter items where product.LayerCode == 0"""
    return [x for x in items if x.WithoutLayerCode()]


def with_amount_remaining(items: Iterable[Item]) -> List[Item]:
    """Filter items that have amount remaining"""
    return [x for x in items if x.HasAmountRemaining()]


def with_amount_remaining_or_detached_amount(items: Iterable[Item]) -> List[Item]:
    """
    C#: items.Where(x => x.HasAmountRemaining() || x.HasDetachedAmount() || 
        (x.Product is IBoxTemplate) && ((IBoxTemplate)x.Product).ItemsInBox.Any(...))
    """
    return [x for x in items if x.WithAmountRemainingOrDetachedAmount()]


def with_detached_amount(items: Iterable[Item]) -> List[Item]:
    """Filter items where DetachedAmount > 0"""
    return [x for x in items if x.DetachedAmount > 0]


def with_calculate_additional_occupation(items: Iterable[Item]) -> List[Item]:
    """Filter items where product.CalculateAdditionalOccupation is True"""
    return [x for x in items if x.WithCalculateAdditionalOccupation()]


def can_be_palletized(items: Iterable[Item]) -> List[Item]:
    """Filter items where product can be palletized"""
    return [x for x in items if x.CanBePalletized()]


# Ordering methods
def ordered_by_priority_and_amount(items: Iterable[Item]) -> List[Item]:
    """
    C#: items.OrderByDescending(x => x.Product?.PalletSetting?.BulkPriority)
             .ThenByDescending(x => x.Amount)
    """
    return sorted(
        items,
        key=lambda x: (
            -(x.Product.PalletSetting.BulkPriority if x.Product and x.Product.PalletSetting else 0),
            -x.Amount
        )
    )


def ordered_by_priority_and_amount_remaining(items: Iterable[Item]) -> List[Item]:
    """
    C#: items.OrderByDescending(x => x.Product?.PalletSetting?.BulkPriority)
             .ThenByDescending(x => x.AmountRemaining)
    """
    return sorted(
        items,
        key=lambda x: (
            -(x.Product.PalletSetting.BulkPriority if x.Product and x.Product.PalletSetting else 0),
            -x.AmountRemaining
        )
    )


def ordered_by_amount_remaining_desc(items: Iterable[Item]) -> List[Item]:
    """
    C#: items.OrderByDescending(x => x.AmountRemaining)
    """
    return sorted(items, key=lambda x: -x.AmountRemaining)


def ordered_by_returnables_and_group_sub_group(items: List[Item]) -> List[Item]:
    """
    C#: items.OrderByDescending(d => d.IsReturnable())
             .ThenBy(d => d.Product.GroupAndSubGroup)
    """
    return sorted(
        items,
        key=lambda x: (
            -int(x.IsReturnable()),
            x.Product.GroupAndSubGroup if x.Product else 0
        )
    )


# PascalCase aliases for C# compatibility
IsChopp = is_chopp
NotChopp = not_chopp
IsIsotonicWater = is_isotonic_water
NotIsotonicWater = not_isotonic_water
IsReturnable = is_returnable
IsPackage = is_package
IsBoxTemplate = is_box_template
NotMarketplace = not_marketplace
WithConfiguration = with_configuration
WithLayerCode = with_layer_code
WithoutLayerCode = without_layer_code
WithAmountRemaining = with_amount_remaining
WithAmountRemainingOrDetachedAmount = with_amount_remaining_or_detached_amount
WithDetachedAmount = with_detached_amount
WithCalculateAdditionalOccupation = with_calculate_additional_occupation
CanBePalletized = can_be_palletized
OrderedByPriorityAndAmount = ordered_by_priority_and_amount
OrderedByPriorityAndAmountRemaining = ordered_by_priority_and_amount_remaining
OrderedByAmountRemainingDesc = ordered_by_amount_remaining_desc
OrderedByReturnablesAndGroupSubGroup = ordered_by_returnables_and_group_sub_group
