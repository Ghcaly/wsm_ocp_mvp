from typing import Dict, List

class finalResultProcessor:

    """Represents the class that processes the final result and puts it
    into the correct output format
    """
    
    def get_all_items(
        self, 
        orders: Dict[str, Dict]
    ) -> List:
        skus_in_orders = [list(orders[k].keys()) for k in orders.keys()]
        flat_list = [item for sublist in skus_in_orders for item in sublist]
        return list(set(flat_list))

    def join_final_result_caixas(
        self, 
        group_result_caixas: List[Dict]
    )-> Dict[str, int]:
        box_number = 0
        final_result_caixas = {}
        for grc in group_result_caixas:
            for box in grc.keys():
                box_number = box_number + 1
                final_result_caixas[box_number] = grc[box]
        return final_result_caixas

    def join_skus(
        self, 
        skus_to_be_grouped: List[Dict]
    ) -> Dict[str, int]:
        grouped_skus = {}
        for sg in skus_to_be_grouped:
            if sg != {}:
                for s in sg.keys():
                    if s in grouped_skus.keys():
                        grouped_skus[s] = grouped_skus[s] + sg[s]
                    else:
                        grouped_skus[s] = sg[s]
        return grouped_skus 

    def join_final_result(
        self, 
        group_results: List[Dict]
    ) -> Dict[str, Dict]:
        final_result = {"pacotes":{}, "caixas":{}, "nao_paletizados": [{}]}
        group_result_pacotes = [gr["pacotes"] for gr in group_results if gr["pacotes"] != {}]
        group_result_caixas = [gr["caixas"] for gr in group_results if gr["caixas"] != {}]
        group_result_nao_paletizados = [gr["nao_paletizados"][0] for gr in group_results if gr["nao_paletizados"] != [{}]]
        if len(group_result_pacotes) == 1:
            final_result['pacotes'] = group_result_pacotes[0]
        elif len(group_result_pacotes) > 1:
            final_result["pacotes"] = self.join_skus(group_result_pacotes)
        if len(group_result_caixas) == 1:
            final_result['caixas'] = group_result_caixas[0]
        elif len(group_result_caixas) > 1:
            final_result["caixas"] = self.join_final_result_caixas(group_result_caixas)
        if len(group_result_nao_paletizados) == 1:
            final_result['nao_paletizados'] = group_result_nao_paletizados
        elif len(group_result_nao_paletizados) > 1:
            final_result["caixas"] = [self.join_skus(group_result_nao_paletizados)]
        return final_result
