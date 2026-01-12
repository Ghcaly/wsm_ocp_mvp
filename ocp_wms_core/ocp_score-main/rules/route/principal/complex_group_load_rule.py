from domain.factor_converter import FactorConverter
from domain.itemList import ItemList
from rules.route.bulk_pallet_rule import BulkPalletRule
from rules.route.chopp_palletization_rule import ChoppPalletizationRule
from domain.base_rule import BaseRule

class ComplexGroupLoadRule(BaseRule):
    """Faithful port of C# ComplexGroupLoadRule.

    This implementation calls domain/context methods directly (no defensive checks)
    to preserve the C# control flow and semantics.
    """

    PERCENT_OCCUPATION_TO_BLOCK_PALLET = 90

    def __init__(self, factor_converter: FactorConverter = None, bulk_pallet_rule=None, chopp_palletization_rule=None):
        super().__init__()
        self.factor_converter = factor_converter or FactorConverter()
        self.bulk_pallet_rule = BulkPalletRule()
        self.chopp_palletization_rule = ChoppPalletizationRule(FactorConverter())

    def should_execute(self, context, item_predicate=None, mounted_space_predicate=None):
        # Parity with C#: do not execute for AS / CrossDocking contexts
        if context.Kind in ('AS', 'CrossDocking'):
            context.add_execution_log('Regra de cliente complexo executa apenas para mapas rota e mixed')
            return False

        if not context.Settings.get('GroupComplexLoads'):
            context.add_execution_log(f'Regra de cliente complexo desabilitada, mapa {getattr(context, "Number", "")}')
            return False

        clients_quantity = len(set(k for o in context.Orders for i in o.Items for k in i.ClientQuantity.keys()))
        if clients_quantity <= 1:
            context.add_execution_log(f'Regra de cliente complexo não será executada pois existe {clients_quantity} cliente no mapa {getattr(context, "Number", "")}')
            return False

        any_complex = bool(self._get_items_that_can_be_grouped(context))
        context.add_execution_log(f'Cliente complexo: {any_complex}, mapa {getattr(context, "Number", "")}')
        return any_complex

    def execute(self, context):
        # Seleciona o cliente com maior ocupação total (igual ao C#)
        groups = self._get_items_that_can_be_grouped(context)
        if not groups:
            context.add_execution_log('Motivo - Nenhum grupo encontrado, regra não será executada')
            return

        client = sorted(groups, key=lambda g: g['TotalOccupation'], reverse=True)[0]

        mounted_spaces = []

        context.add_execution_log(
            f"Iniciando o processamento de {len(client['Items'])} itens do cliente {client['ClientCode']}"
        )

        # Execução idêntica ao C# --------------------------------------------

        if self.bulk_pallet_rule:
            self.bulk_pallet_rule \
                .with_complex_customer(client['ClientCode']) \
                .execute(context, lambda x: client['ClientCode'] in x.ClientQuantity)

        if self.chopp_palletization_rule:
            self.chopp_palletization_rule \
                .with_complex_customer(client['ClientCode']) \
                .without_group_limit() \
                .execute(context, lambda x: client['ClientCode'] in x.ClientQuantity)

        # O C# percorre os itens NA ORDEM RECEBIDA
        for item in client['Items']:
            self._mount_complex_space(context, client, mounted_spaces, item)

        # Bloquear paletes com ocupação >= limite
        for m in context.MountedSpaces:
            if m.OccupiedPercentage >= self.PERCENT_OCCUPATION_TO_BLOCK_PALLET:
                m.Block()

    # def _get_items_that_can_be_grouped(self, context):
    #     not_full = context.GetNotFullSpaces()
    #     if not not_full:
    #         return []

    #     smaller_space = sorted(list(not_full), key=lambda s: int(s.Size), reverse=True)[0]

    #     clients = sorted(list(set(k for o in context.Orders for i in o.Items for k in i.ClientQuantity.keys())))
    #     grouped_loads = []
    #     for client in clients:
    #         items = [it for o in context.Orders for it in ItemList(o.Items).CanBePalletized() if client in it.ClientQuantity]
            
    #         sku_quantity = len(set(it.Code for it in items))
    #         if sku_quantity < context.Settings.get('QuantitySkuInComplexLoads'):
    #             context.add_execution_log(f"Cliente: {client}, não atende a configuração de quantidade mínima de skus de {context.Settings.get('QuantitySkuInComplexLoads')}, SKUS {sku_quantity}")
    #             continue

    #         total_occupation = sum(self.factor_converter.Occupation(it.ClientQuantity[client], smaller_space.Size, it, context.Settings.get('OccupationAdjustmentToPreventExcessHeight')) for it in items)
    #         if total_occupation < context.Settings.get('MinimumVolumeInComplexLoads'):
    #             context.add_execution_log(f"Cliente: {client}, não atende a configuração de volume minimo no pallet complexo {context.Settings.get('MinimumVolumeInComplexLoads')}, ocupacao: {total_occupation}")
    #             continue

    #         grouped_loads.append({
    #             'Items': items,
    #             'ClientCode': client,
    #             'TotalOccupation': total_occupation,
    #             'SkuQuantity': sku_quantity
    #         })

    #     return grouped_loads
    
    def _get_items_that_can_be_grouped(self, context):

        # 1. Obter menor espaço
        not_full = context.GetNotFullSpaces()
        if not not_full:
            return []

        smaller_space = sorted(not_full, key=lambda s: int(s.Size), reverse=True)[0]

        # 2. Obter clientes distintos
        clients = list({
            k
            for order in context.Orders
            for item in order.Items
            for k in item.ClientQuantity.keys()
        })

        grouped_loads = []

        # 3. Percorrer clientes
        for client in clients:

            # ----- CÓPIA EXATA DO C# -----
            # Primeiro filtra ORDENS
            valid_orders = [
                o for o in context.Orders
                if any(
                    client in it.ClientQuantity
                    for it in ItemList(o.Items).CanBePalletized()
                )
            ]

            # Agora obtém ITENS dessas ordens
            items = [
                it
                for o in valid_orders
                for it in ItemList(o.Items).CanBePalletized()
                if client in it.ClientQuantity
            ]
            # ----- FIM DA CÓPIA EQUIVALENTE -----

            # Se não houver itens, ignora
            if not items:
                continue

            # Quantidade de SKUs
            sku_quantity = len({it.Code for it in items})
            min_sku = context.Settings.get("QuantitySkuInComplexLoads")

            if sku_quantity < min_sku:
                context.add_execution_log(
                    f"Cliente: {client}, não atende a configuração de quantidade mínima de skus "
                    f"de {min_sku}, SKUS {sku_quantity}"
                )
                continue

            # Soma da ocupação (igual ao C#)
            adj = context.Settings.get("OccupationAdjustmentToPreventExcessHeight")
            total_occupation = sum(
                self.factor_converter.Occupation(
                    it.ClientQuantity[client],
                    smaller_space.Size,
                    it,
                    adj
                ) for it in items
            )

            min_volume = context.Settings.get("MinimumVolumeInComplexLoads")

            if total_occupation < min_volume:
                context.add_execution_log(
                    f"Cliente: {client}, não atende a configuração de volume minimo no pallet complexo "
                    f"{min_volume}, ocupacao: {total_occupation}"
                )
                continue

            grouped_loads.append({
                "Items": items,
                "ClientCode": client,
                "TotalOccupation": total_occupation,
                "SkuQuantity": sku_quantity
            })

        return grouped_loads


    def _mount_complex_space(self, context, client_group, mounted_spaces, item):
        """Corresponds to the C# MountComplexSpace method."""
        palletized_mounted_space = None
        space = None
        retries = 0

        while True:
            context.add_execution_log(f"Loop Complex Group Rule nº {retries}")

            # Recompute current remaining for this client; exit if zero
            current_remaining = item.ClientQuantity[client_group['ClientCode']]
            if current_remaining <= 0:
                break

            if not mounted_spaces:
                space = self._get_next_space(context)
            else:
                candidate_space = None
                # Find a mounted space with enough OccupationRemaining
                sorted_ms = sorted(mounted_spaces, key=lambda m: m.OccupationRemaining)
                for ms in sorted_ms:
                    needed_occupation = self.factor_converter.Occupation(item.ClientQuantity[client_group['ClientCode']], ms.Space.Size, item, context.Settings.get('OccupationAdjustmentToPreventExcessHeight'))
                    if ms.OccupationRemaining >= needed_occupation:
                        candidate_space = ms.Space
                        break
                space = candidate_space or self._get_next_space(context)

            if space is None:
                break

            prev_remaining = current_remaining
            palletized_mounted_space = self._mount_product(client_group['ClientCode'], context, space, item)

            if palletized_mounted_space and palletized_mounted_space not in mounted_spaces:
                mounted_spaces.append(palletized_mounted_space)

            retries += 1
            # Break condition from C# do-while
            if palletized_mounted_space is None or space is None or item.ClientQuantity[client_group['ClientCode']] <= 0:
                break

            # If no progress on remaining quantity, avoid repeating same add
            if item.ClientQuantity[client_group['ClientCode']] == prev_remaining:
                break

    # def _get_next_space(self, context):
    #     """Returns the next available, unmounted space, preferring larger bays and Helper side first."""
    #     mounted_space_numbers = {ms.Space.Number for ms in context.MountedSpaces}

    #     # Filter out already mounted spaces
    #     available_spaces = [s for s in context.Spaces if s.Number not in mounted_space_numbers]
    #     if not available_spaces:
    #         return None

    #     # Sort by Size asc, Number asc, then Side (as in C#)
    #     sorted_spaces = sorted(available_spaces, key=lambda x: (int(x.Size), int(x.Number), getattr(x, 'Side', 0)))

    #     return sorted_spaces[0] if sorted_spaces else None

    def _get_next_space(self, context):
        """
        Python equivalent of:
            context.Spaces
                .OrderBy(x => (int)x.Size)
                .ThenBy(x => x.Number)
                .ThenBy(x => ((ITruckBayRoute)x).Side)
                .FirstOrDefault();
        """

        spaces = list(context.Spaces)

        if not spaces:
            return None

        sorted_spaces = sorted(
            spaces,
            key=lambda x: (
                int(x.Size),
                x.Number,
                getattr(x, "Side", None)  # matches ((ITruckBayRoute)x).Side
            )
        )

        return sorted_spaces[0]

    # No helper required; C# uses space sizes directly when calculating occupation.

    def _mount_product(self, client, context, space, item):
        """Corresponds to the C# MountProduct method."""
        mounted_space = context.GetMountedSpace(space)
        factor = item.Product.GetFactor(space.Size)

        quantity = item.ClientQuantity[client]
        if mounted_space is None:
            factor_quantity = int(self.factor_converter.QuantityPerFactor(int(space.Size), quantity, factor, item, context.Settings.get('OccupationAdjustmentToPreventExcessHeight')))
            if factor_quantity < quantity:
                quantity = factor_quantity
        else:
            quantity = int(self.factor_converter.QuantityToRemainingSpace(mounted_space, item, quantity, context.Settings))

        occupation = self.factor_converter.Occupation(quantity, factor, item.Product.PalletSetting, item, context.Settings.get('OccupationAdjustmentToPreventExcessHeight'))

        remaining_occupation = int(space.Size) - (mounted_space.Occupation if mounted_space else 0)
        if quantity == 0 or occupation > remaining_occupation:
            return None

        context.add_execution_log(f"Adicionando o item {item.Code} na baia {space.Number} / {space.sideDesc}, quantidade: {quantity} ocupacao: {occupation}")

        new_mounted_space = context.AddComplexLoadProduct(space, item, quantity, occupation, client)
        for container in new_mounted_space.Containers:
            container.Block()

        # In C# the context operation mutates state as needed; rely on context.AddComplexLoadProduct side-effects.

        return new_mounted_space
