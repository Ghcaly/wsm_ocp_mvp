from typing import List
from ...domain.base_rule import BaseRule
from ...domain.order import Order
from ...domain.context import Context

class T4MixedRule(BaseRule):
    """
    O propósito principal da `T4MixedRule` é analisar, processar e otimizar 
    operações do tipo T4 que apresentam características mistas. 
    Esta regra identifica, organiza e configura produtos em operações T4, 
    aplicando estratégias específicas para este tipo de carregamento e garantindo 
    uma abordagem eficiente e especializada..
    
    Lógica:
    1. Para cada order, executa loop de tentativas até não ter mais espaço ou itens
    2. Em cada tentativa: NumberOfPalletsRule → BaysNeededRule → MixedRulesChain
    3. Controla tentativas (attempt) e verifica espaços disponíveis
    """
    
    def __init__(self, bays_needed_rule=None, number_of_pallets_rule=None):
        """
        Inicializa com dependências:
        - IBaysNeededRule _baysNeededRule
        - INumberOfPalletsRule _numberOfPalletsRule
        - IMixedRulesFactory _mixedRulesFactory (implementação futura)
        """
        self.bays_needed_rule = bays_needed_rule
        self.number_of_pallets_rule = number_of_pallets_rule

    def execute(self, context: Context):
        """
        Implementa a lógica principal do T4MixedRule:
        """
        print("[T4MixedRule] Paletizando os itens")
        
        orders = self._get_orders(context)
        
        if not orders:
            print("[T4MixedRule] Nenhuma ordem para executar")
            return
        
        new_context = context.copy()
        
        for order in orders:
            print(f"[T4MixedRule] Processando order {order.id}")
            
            old_sum_of_amount = 1
            sum_of_amount = 0
            attempt = 0
            retries = 0
            
            # Loop principal: continua enquanto há espaço e itens não paletizados
            while self._has_space_and_not_palletized_items(new_context, order) and old_sum_of_amount != sum_of_amount:
                print(f"[T4MixedRule] Loop Mixed Rule nº {retries}")
                
                # Criar cadeia de regras mistas
                mixed_rules_chain = self._create_mixed_rules_chain(new_context)
                
                # Limpar filtros
                new_context.clear_filters()
                
                # Verificar se ainda há espaços disponíveis
                if not getattr(new_context, 'spaces', []):
                    print("[T4MixedRule] Nenhum espaço disponível, interrompendo")
                    break
                
                # Guarda quantidade antiga de itens restantes
                old_sum_of_amount = self._get_items_palletizable_sum(order)
                
                # Define espaços adicionais baseado na tentativa
                self._set_additional_spaces(order, attempt)
                
                # Filtra contexto para apenas esta order
                new_context.with_only_order(order)
                
                # Executa cadeia de regras: NumberOfPallets → BaysNeeded → MixedRules
                if self.number_of_pallets_rule:
                    new_context = self.number_of_pallets_rule.execute(new_context)
                
                if self.bays_needed_rule:
                    new_context = self.bays_needed_rule.execute_chain(new_context)
                
                if mixed_rules_chain:
                    new_context = mixed_rules_chain.execute_chain(new_context)
                
                # Limpar filtros novamente
                new_context.clear_filters()
                
                # Verifica nova quantidade de itens restantes
                sum_of_amount = self._get_items_palletizable_sum(order)
                
                attempt += 1
                retries += 1
                
                print(f"[T4MixedRule] Tentativa {attempt}: {old_sum_of_amount} → {sum_of_amount}")
        
        # Atualiza contexto com as mudanças
        self._change_context(new_context, context)
        print("[T4MixedRule] Paletização T4 Mixed concluída")
    
    def _get_orders(self, context: Context) -> List[Order]:
        """
        Obtém todas as orders do contexto
        """
        return getattr(context, 'orders', [])
    
    def _has_space_and_not_palletized_items(self, context: Context, order: Order) -> bool:
        """
        Verifica se há espaço disponível e itens não paletizados para a order.
        """
        spaces = getattr(context, 'spaces', [])
        has_space = len(spaces) >= 1
        
        palletizable_items = self._get_items_palletizable_by_order(context, order)
        has_items = any(item for item in palletizable_items if getattr(item, 'amount_remaining', 1) > 0)
        
        return has_space and has_items
    
    def _get_items_palletizable_by_order(self, context: Context, order: Order) -> List:
        """
        Obtém itens paletizáveis da order
        """
        # Simplificação: retorna products da order
        return getattr(order, 'products', [])
    
    def _get_items_palletizable_sum(self, order: Order) -> int:
        """
        Soma quantidade restante dos itens paletizáveis.
        """
        items = getattr(order, 'products', [])
        return sum(getattr(item, 'amount_remaining', getattr(item, 'quantity', 1)) for item in items)
    
    def _set_additional_spaces(self, order: Order, attempt: int):
        """
        Define espaços adicionais baseado na tentativa
        """
        order.set_additional_spaces(attempt)
    
    def _create_mixed_rules_chain(self, context: Context):
        """
        Cria cadeia de regras mistas baseado no MixedRulesFactory C#:
    
        Cadeia: MixedASRule → MixedRouteRule → MixedRemountRule
        """
        print("[T4MixedRule] Criando cadeia de regras mistas:")
        print("[T4MixedRule] - MixedASRule → MixedRouteRule → MixedRemountRule")
        print("[T4MixedRule] (implementação completa futura)")
        
        # Por enquanto, retorna None - implementação futura das regras Mixed
        return None
    
    def _change_context(self, new_context: Context, original_context: Context):
        """
        Atualiza contexto original com mudanças do novo contexto
        """
        # Transfere pallets criados
        if hasattr(new_context, 'pallets') and hasattr(original_context, 'pallets'):
            for pallet in new_context.pallets:
                if pallet not in original_context.pallets:
                    original_context.add_pallet(pallet)
                    print(f"[T4MixedRule] Pallet transferido: {pallet}")
