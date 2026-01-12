from domain.container_type import ContainerType
from domain.mounted_space_list import MountedSpaceList
from domain.itemList import ItemList
from domain.base_rule import BaseRule


class ReturnableAndDisposableSplitRemountRule(BaseRule):
    """Python port of C# ReturnableAndDisposableSplitRemountRule.

    This port calls domain helpers and object attributes directly as in the
    original C# code (no defensive existence checks), and mirrors the
    original four join steps in separate helper methods.
    """

    def __init__(self, factor_converter=None):
        super().__init__()
        self.factor_converter = factor_converter

    def _get_items(self, context, item_predicate=None):
        item_predicate = item_predicate or self.get_default_item_predicate()    
        return ItemList(context.get_items()).NotMarketplace().matching(item_predicate).ordered_by_amount_remaining_desc()
        # items = 
        # if item_predicate:
        #     items = [i for i in items if item_predicate(i)]

        # # NotMarketplace().Where(itemPredicate).OrderedByAmountRemainingDesc()
        # filtered = [i for i in items if not i.is_marketplace and not i.is_chopp and not i.is_isotonic_water and i.amount_remaining > 0]
        # return sorted(filtered, key=lambda x: x.amount_remaining, reverse=True)

    def get_default_item_predicate(self):
        return lambda x: x.NotChopp() and x.NotIsotonicWater() and x.HasAmountRemaining()

    def should_execute(self, context, item_predicate=None, mounted_space_predicate=None):
        item_predicate = item_predicate or self.get_default_item_predicate()
        items = self._get_items(context, item_predicate)
        if not items:
            context.add_execution_log("Nenhum item elegivel para remount encontrado, pulando regra de remount.")
            return False
        return True

    def execute(self, context, item_predicate=None, mounted_space_predicate=None):
        item_predicate = item_predicate or self.get_default_item_predicate()
        items = self._get_items(context, item_predicate)
        if not items:
            return
                
        mounted_spaces_not_chopp = context.MountedSpaces.HasSpaceAndNotBlocked().NotChopp().to_list()
        mounted_spaces_chopp = context.MountedSpaces.HasSpaceAndNotBlocked().IsChopp().NotKegExclusive().to_list()

        ops = context.domain_operations

        # Step 1
        self._join_into_similar_packing_group_with_different_type(context, items, mounted_spaces_not_chopp, ops)
        if not any(i.amount_remaining for i in items):
            return

        # Step 2
        self._join_into_disposable_and_returnable_pairs(context, items, mounted_spaces_not_chopp, ops)
        if not any(i.amount_remaining for i in items):
            return

        # Step 3
        self._join_into_chopp_mounted_spaces(context, items, mounted_spaces_chopp, ops)
        if not any(i.amount_remaining for i in items):
            return

        # Step 4
        self._join_same_type_and_chopp(context, items, mounted_spaces_not_chopp, mounted_spaces_chopp, ops)

    # --- helper steps -----------------------------------------------------
    def _join_into_similar_packing_group_with_different_type(self, context, items, mounted_spaces_not_chopp, ops):
        for item in ItemList(items).OrderedByAmountRemainingDesc():

            similarMountedSpaces = MountedSpaceList(mounted_spaces_not_chopp)\
                                    .WithSameType( ContainerType.DISPOSABLE if item.Product.ContainerType == ContainerType.RETURNABLE
                                                    else ContainerType.RETURNABLE).OrderByLayerAndDifferenceAndOccupation(item.Product)


            if (item.Product.NotReturnable()):
                    similarMountedSpaces = MountedSpaceList(similarMountedSpaces).OrderByRemountDescAndOccupation()

            for ms in similarMountedSpaces:
                ops.add_amount_remaining_item_into_mounted_space(context, item, ms)
                if item.amount_remaining == 0:
                    context.add_execution_log(f"Adicionado o item {item.Code} - {item.Product.Name} na baia {ms.Space.Number} / {ms.Space.sideDesc}, na quantidade {item.amount_remaining} ficando com a ocupacao de {ms.Occupation}")
                    break

    def _join_into_disposable_and_returnable_pairs(self, context, items, mounted_spaces_not_chopp, ops):
        for item in ItemList(items).OrderedByAmountRemainingDesc():

            disposableMountedSpace = MountedSpaceList(mounted_spaces_not_chopp)\
                .WithSameType(ContainerType.DISPOSABLE).OrderByLayerAndDifference(item.Product)\
                    .first_or_default()

            returnableMountedSpaces = MountedSpaceList(mounted_spaces_not_chopp)\
                .WithSameType(ContainerType.RETURNABLE).OrderByLayerAndDifferenceAndOccupation(item.Product)

            if not item.Product.is_returnable():
                returnableMountedSpaces = returnableMountedSpaces.OrderByRemountDescAndOccupation()

            if disposableMountedSpace is not None and MountedSpaceList(returnableMountedSpaces).any():
                for r in returnableMountedSpaces:
                    ops.add_on_2_spaces(context, disposableMountedSpace.space, r.space, item)
                    if item.amount_remaining == 0:
                        context.add_execution_log(f"Adicionado o item {item.Code} - {item.Product.Name} na baia {disposableMountedSpace.Space.Number} / {disposableMountedSpace.Space.sideDesc}, na quantidade {item.amount_remaining} ficando com a ocupacao de {disposableMountedSpace.Occupation}")
                        break

               
    def _join_into_chopp_mounted_spaces(self, context, items, mounted_spaces_chopp, ops):
        for item in ItemList(items).OrderedByAmountRemainingDesc():
            for ch in MountedSpaceList(mounted_spaces_chopp).OrderByRemountDescAndOccupation():
                ops.add_amount_remaining_item_into_mounted_space(context, item, ch)
                if item.amount_remaining == 0:
                    context.add_execution_log(f"Adicionado o item {item.Code} - {item.Product.Name} na baia {ch.Space.Number} / {ch.Space.sideDesc}, na quantidade {item.amount_remaining} ficando com a ocupacao de {ch.Occupation}")
                    break

    def _join_same_type_and_chopp(self, context, items, mounted_spaces_not_chopp, mounted_spaces_chopp, ops):
        for item in ItemList(items).OrderedByAmountRemainingDesc():

            similarMountedSpaceNotChopp = MountedSpaceList(mounted_spaces_not_chopp).WithSameType( ContainerType.RETURNABLE if item.Product.ContainerType == ContainerType.RETURNABLE
                else ContainerType.DISPOSABLE).OrderByLayerAndDifference(item.Product)\
                    .first_or_default()
                                                                                            
            similarMountedSpacesChopp = MountedSpaceList(mounted_spaces_chopp).OrderByLayerRemountDescAndOccupation()

            if similarMountedSpaceNotChopp is not None and MountedSpaceList(similarMountedSpacesChopp).any():
                for ch in similarMountedSpacesChopp:
                    ops.add_on_2_spaces(context, similarMountedSpaceNotChopp.space, ch.space, item)
                    if item.amount_remaining == 0:
                        context.add_execution_log(f"Adicionado o item {item.Code} - {item.Product.Name} na baia {similarMountedSpaceNotChopp.Space.Number} / {similarMountedSpaceNotChopp.Space.sideDesc}, na quantidade {item.amount_remaining} ficando com a ocupacao de {similarMountedSpaceNotChopp.Occupation}")
                        break
