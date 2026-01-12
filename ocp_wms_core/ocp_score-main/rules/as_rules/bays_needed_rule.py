import json
import os
import sys

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    
from domain.base_rule import BaseRule
# from domain import Order, Pallet, ItemPallet
from domain.context import Context
from typing import List
from decimal import Decimal

class BaysNeededRule(BaseRule):
    MAXIMUM_FRACTIONAL_VALUE_TO_ROUND = Decimal('0.01')
    MINIMUM_FRACTIONAL_VALUE_TO_ROUND = Decimal('0.99')

    def __init__(self):
        pass

    def execute(self, context: Context):
        """
        Implementa a lógica principal da regra BaysNeeded similar ao C#:
        1. Calcula a quantidade total de baias necessárias
        2. Atualiza a quantidade de pallets necessários por pedido
        3. Ajusta valores fracionais conforme regras de arredondamento
        """
        print("Executando BaysNeededRule...")
        
        # 1. Calcula a quantidade total de baias necessárias para o mapa
        amount_bays_needed_to_map = self.get_amount_bays_needed_to_map(context)
        print(f"Quantidade total de baias necessárias: {amount_bays_needed_to_map}")
        
        # 2. Atualiza a quantidade de pallets necessários por pedido (arredonda frações pequenas)
        self.update_amount_bays_needed_by_order(context)
        
        # 3. Atualiza valores arredondados baseados no total calculado
        self.update_amount_bays_needed_rounded_by_order(context, amount_bays_needed_to_map)
        
        # 4. Log da execução
        total_orders = len(getattr(context, 'orders', []))
        print(f"Processados {total_orders} pedidos na regra BaysNeeded")

    def get_amount_bays_needed_to_map(self, context: Context) -> Decimal:
        amount_bays_needed_to_map = sum(order.quantity_of_pallets_needed for order in context.orders)
        amount_bays_needed_without_fractional = int(amount_bays_needed_to_map)
        fractional_amount_bays_needed_to_map = amount_bays_needed_to_map - amount_bays_needed_without_fractional
        if (fractional_amount_bays_needed_to_map > self.MAXIMUM_FRACTIONAL_VALUE_TO_ROUND and
            fractional_amount_bays_needed_to_map < self.MINIMUM_FRACTIONAL_VALUE_TO_ROUND):
            return amount_bays_needed_to_map
        else:
            return self.round_to_upper(amount_bays_needed_to_map)

    def update_amount_bays_needed_by_order(self, context: Context):
        for order in context.orders:
            fractional = order.quantity_of_pallets_needed - int(order.quantity_of_pallets_needed)
            if (fractional <= self.MAXIMUM_FRACTIONAL_VALUE_TO_ROUND or
                fractional >= self.MINIMUM_FRACTIONAL_VALUE_TO_ROUND):
                # print(f"Arredondando pedido {order.id} de {order.quantity_of_pallets_needed} para cima.")
                order.set_quantity_of_pallets_needed(self.round_to_upper(order.quantity_of_pallets_needed))

    def update_amount_bays_needed_rounded_by_order(self, context: Context, amount_bays_needed_to_map: Decimal):
        """
        Atualiza os valores arredondados de pallets necessários por pedido
        baseado na quantidade total de baias calculadas para o mapa
        """
        print("Atualizando valores arredondados por pedido...")
        self.set_amount_rounded_to_upper(context)
        self.adjust_amount_rounded_to_fit(context, amount_bays_needed_to_map)

    def set_amount_rounded_to_upper(self, context: Context):
        """
        Define os valores arredondados para cima para cada pedido.
        Equivalente ao SetAmountRoundedToUpper do C#
        """
        print("Definindo valores arredondados para cima...")
        for order in context.orders:
            order.quantity_of_pallets_needed_rounded = self.round_to_upper(order.quantity_of_pallets_needed)
            
            # print(f"Pedido {order.id}: Original={order.quantity_of_pallets_needed}, Arredondado={order.quantity_of_pallets_needed_rounded}")

    def adjust_amount_rounded_to_fit(self, context: Context, amount_bays_needed_to_map: Decimal):
        """
        Ajusta os valores arredondados para se adequar ao total de baias necessárias.
        Equivalente ao AdjustAmountRoundedToFit do C#
        """
        print(f"Ajustando valores para se adequar ao total: {amount_bays_needed_to_map}")
        
        # Calcula o total atual dos valores arredondados
        total_rounded = sum(
            getattr(order, 'quantity_of_pallets_needed_rounded', self.round_to_upper(order.quantity_of_pallets_needed))
            for order in context.orders
        )
        
        print(f"Total arredondado atual: {total_rounded}")
        
        # Se o total arredondado for maior que o necessário, ajusta para baixo
        if total_rounded > amount_bays_needed_to_map:
            difference = total_rounded - amount_bays_needed_to_map
            print(f"Diferença a ajustar: {difference}")
            
            # Ordena os pedidos por diferença entre original e arredondado (menor diferença primeiro)
            orders_to_adjust = []
            for order in context.orders:
                original = order.quantity_of_pallets_needed
                rounded = getattr(order, 'quantity_of_pallets_needed_rounded', self.round_to_upper(original))
                diff = rounded - original
                if diff > 0:  # Só considera pedidos que foram arredondados para cima
                    orders_to_adjust.append((order, diff))
            
            # Ordena por menor diferença (mais fáceis de ajustar)
            orders_to_adjust.sort(key=lambda x: x[1])
            
            # Ajusta os pedidos até atingir o total desejado
            remaining_adjustment = difference
            for order, diff in orders_to_adjust:
                if remaining_adjustment <= 0:
                    break
                
                # Calcula quanto pode reduzir deste pedido
                max_reduction = min(remaining_adjustment, diff)
                old_rounded = order.quantity_of_pallets_needed_rounded
                order.quantity_of_pallets_needed_rounded = old_rounded - max_reduction
                remaining_adjustment -= max_reduction
                
                # print(f"Ajustado pedido {order.id}: {old_rounded} -> {order.quantity_of_pallets_needed_rounded}")
        
        # Log final
        final_total = sum(
            getattr(order, 'quantity_of_pallets_needed_rounded', order.quantity_of_pallets_needed)
            for order in context.orders
        )
        print(f"Total final ajustado: {final_total}")

    @staticmethod
    def round_to_upper(value: Decimal) -> Decimal:
        return Decimal(int(value) + (1 if value % 1 > 0 else 0))
