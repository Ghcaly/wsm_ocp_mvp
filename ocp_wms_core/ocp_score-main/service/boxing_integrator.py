#!/usr/bin/env python3
"""
Boxing API Integrator

Integra com wms-itemsboxing API para processamento de produtos marketplace.
"""

import requests
import logging
from typing import Dict, Any, List
import json

log = logging.getLogger(__name__)


class BoxingIntegrator:
    """Integra com a API de boxing (wms-itemsboxing)"""
    
    def __init__(self, boxing_api_url: str = "http://localhost:8001"):
        """
        Inicializa o integrador
        
        Args:
            boxing_api_url: URL base da API de boxing
        """
        self.api_url = boxing_api_url
        self.endpoint = f"{boxing_api_url}/api/items-boxing/calculate/"
    
    def check_health(self) -> bool:
        """Verifica se a API de boxing está online"""
        try:
            response = requests.get(f"{self.api_url}/api/items-boxing/health/", timeout=5)
            return response.status_code == 200
        except Exception as e:
            log.error(f"Boxing API não está disponível: {e}")
            return False
    
    def format_input_for_boxing(self, marketplace_items: List[Dict], 
                                 product_dimensions: Dict = None) -> Dict:
        """
        Formata itens marketplace para o formato esperado pela API de boxing
        
        Args:
            marketplace_items: Lista de itens marketplace
            product_dimensions: Dict com dimensões dos produtos {sku: {length, width, height, ...}}
            
        Returns:
            Dict no formato esperado pela API de boxing
        """
        # Agrupa itens por pedido (se tiver campo Order/OrderId)
        orders = {}
        skus_info = {}
        
        for item in marketplace_items:
            # Extrai informações do item
            code = str(item.get('Code') or item.get('ProductCode') or item.get('SKU', ''))
            quantity = item.get('Quantity', 0)
            order_id = item.get('OrderId', '0')
            
            # Agrupa por pedido
            if order_id not in orders:
                orders[order_id] = {}
            
            if code not in orders[order_id]:
                orders[order_id][code] = 0
            orders[order_id][code] += quantity
            
            # Coleta dimensões se disponíveis
            if code not in skus_info:
                if product_dimensions and code in product_dimensions:
                    skus_info[code] = product_dimensions[code]
                else:
                    # Dimensões padrão se não tiver
                    skus_info[code] = {
                        'length': item.get('Length', 10.0),
                        'width': item.get('Width', 10.0),
                        'height': item.get('Height', 20.0),
                        'units_in_boxes': item.get('UnitsPerBox', 12),
                        'tipo_garrafa': 0 if 'CAIXA' in item.get('Description', '').upper() else 1
                    }
        
        # Monta estrutura de caixas padrão
        boxes = {
            "1": {  # Garrafeira
                "length": 0,
                "width": 0,
                "height": 0,
                "box_slots": 9,
                "box_slot_diameter": 10.392304
            },
            "2": {  # Caixa
                "length": 40,
                "width": 58,
                "height": 34,
                "box_slots": 0,
                "box_slot_diameter": 0
            }
        }
        
        boxing_input = {
            "orders": orders,
            "skus": skus_info,
            "boxes": boxes
        }
        
        return boxing_input
    
    def process_boxing(self, marketplace_items: List[Dict], 
                       product_dimensions: Dict = None) -> Dict:
        """
        Processa itens marketplace através da API de boxing
        
        Args:
            marketplace_items: Lista de itens marketplace
            product_dimensions: Dimensões dos produtos
            
        Returns:
            Resultado do boxing com pacotes, caixas e não paletizados
        """
        if not marketplace_items:
            log.info("Nenhum item marketplace para processar")
            return None
        
        # Verifica se API está disponível
        if not self.check_health():
            log.warning("Boxing API não disponível, pulando processamento")
            return None
        
        try:
            # Formata input
            boxing_input = self.format_input_for_boxing(marketplace_items, product_dimensions)
            
            log.info(f"Enviando {len(marketplace_items)} itens marketplace para boxing API...")
            
            # Chama API
            response = requests.post(
                self.endpoint,
                json=boxing_input,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                log.info(f"✓ Boxing processado com sucesso")
                
                # Log resumo
                if 'pacotes' in result:
                    log.info(f"  - Pacotes: {len(result.get('pacotes', {}))}")
                if 'caixas' in result:
                    log.info(f"  - Caixas: {len(result.get('caixas', {}))}")
                if 'nao_paletizados' in result:
                    log.info(f"  - Não paletizados: {len(result.get('nao_paletizados', []))}")
                
                return result
            else:
                log.error(f"Erro na Boxing API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            log.error(f"Erro ao processar boxing: {e}")
            return None
    
    def integrate_boxing_result_into_palletization(self, 
                                                    boxing_result: Dict,
                                                    context: Any) -> None:
        """
        Integra resultado do boxing no contexto de paletização
        
        Args:
            boxing_result: Resultado da API de boxing
            context: Context do ocp_wms_core
        """
        if not boxing_result:
            return
        
        # TODO: Implementar lógica de integração baseada nas regras de negócio
        # Por enquanto, apenas loga
        log.info("Integrando resultado do boxing no contexto de paletização...")
        
        # Possíveis ações:
        # - Criar paletes específicos para marketplace
        # - Marcar itens como pré-empacotados
        # - Ajustar ocupação de espaços
        # - Aplicar restrições especiais
        
        pass


# Singleton global
_integrator_instance = None

def get_integrator() -> BoxingIntegrator:
    """Retorna instância singleton do integrador"""
    global _integrator_instance
    if _integrator_instance is None:
        _integrator_instance = BoxingIntegrator()
    return _integrator_instance


if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.INFO)
    
    integrator = BoxingIntegrator()
    
    print(f"\n✓ Boxing API Health Check: {integrator.check_health()}")
    
    # Teste com dados fictícios
    test_items = [
        {
            'Code': '1706',
            'ProductCode': '1706',
            'Quantity': 20,
            'OrderId': '1',
            'Description': 'LIZA OLEO DE GIRASSOL',
            'Length': 9.0,
            'Width': 9.0,
            'Height': 27.0
        }
    ]
    
    formatted = integrator.format_input_for_boxing(test_items)
    print(f"\n✓ Input formatado:")
    print(json.dumps(formatted, indent=2))
