from ...domain.itemList import ItemList
from ...domain.base_rule import BaseRule

class BulkPalletAdditionalOccupationRule(BaseRule):
    def __init__(self, factor_converter = None):
        super().__init__()
        self.factor_converter = factor_converter 

    def should_execute(self, context, item_predicate=None, mounted_space_predicate=None):
        # Segue a lógica do C# ShouldExecute
        if not context.get_setting('OccupationAdjustmentToPreventExcessHeight', False):
            context.add_execution_log(f"Motivo - Configuração 'OccupationAdjustmentToPreventExcessHeight' está desabilitada")
            return False

        # Assume que context.spaces tem método any()/Any()
        if not context.spaces.any():
            context.add_execution_log(f"Motivo - Nenhuma baia vazia disponível no caminhão")
            return False

        return True

    def execute(self, context, item_predicate=None, mounted_space_predicate=None):
        items = ItemList(context.get_items()).matching(item_predicate) \
                            .WithCalculateAdditionalOccupation().NotChopp()\
                            .NotMarketplace().WithAmountRemaining()\
                            .ordered_by_priority_and_amount_remaining()
        
        context.add_execution_log(f"Iniciando o processamento de {len(items)} itens")

        for item in items:
            bays = context.domain_operations.ordered_by(context.spaces, fields=["size", "number"])
            context.add_execution_log(f"Numero de baias do caminhao: {len(bays)}")
            for space in bays:
                self._add_bulk_pallet_with_additional_occupation(context, item, space)


    def _add_bulk_pallet_with_additional_occupation(self, context, item, space):
        # calcula ocupação total se colocarmos todo o restante do item
        total_occupation = self.factor_converter.occupation(item.amount_remaining, space.size, item, True)

        if total_occupation < space.size:
            return

        context.add_execution_log(f"Tentando adicionar o Item {item.code}, Quantidade {item.amount_remaining} na Baia {space.number}/{getattr(space, 'side', '')}, OcupacaoTotal({total_occupation})")

        # calcula a quantidade que cabe na baia (seguindo a chamada do C#)
        quantity = int(self.factor_converter.quantity_to_remaining_space(space.size, space.size, item, context.settings))

        # verifica se pode adicionar (assume que context_actions existe e tem can_add)
        if not context.domain_operations.can_add(context, space, item, quantity):
            context.add_execution_log(f"Não foi possivel adicionar o Item {item.code}, Quantidade {quantity} na Baia ({space.number}/{getattr(space, 'side', '')})")
            return

        # recalcula ocupação para a quantidade que será adicionada e adiciona o produto
        total_occupation = self.factor_converter.occupation(quantity, space.size, item, True)
        context.add_product(space, item, quantity, total_occupation)

        product_occupation = total_occupation - item.additional_occupation
        context.add_execution_log(f"Adicionado o Item {item.code}, Quantidade {quantity}, Baia {space.number}/{getattr(space, 'side', '')}, Ocupação do produto ({product_occupation}), Ocupação adicional ({item.additional_occupation})")
