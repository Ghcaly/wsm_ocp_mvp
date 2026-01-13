

import unittest

class TCompareSKUsQts(unittest.TestCase):

    """Represents a class to test the algorithm output and make sure all the SKUs in the 
    input are in the output with their respective quantities.
    """

    def group_skus_input(self, map_input):
        grouped_skus_input = {}
        for client_order in map_input:
            for sku in map_input[client_order]:
                if sku in list(grouped_skus_input.keys()):
                    grouped_skus_input[sku] = grouped_skus_input[sku] + int(map_input[client_order][sku])
                else:
                    grouped_skus_input[sku] = int(map_input[client_order][sku])
        return grouped_skus_input

    def group_skus_output_caixas(self, map_output_caixas, grouped_skus_output):
        for box_number in list(map_output_caixas.keys()):
            box = map_output_caixas[box_number]
            box_type = list(box.keys())[0]
            for sku in box[box_type]:
                if sku in list(grouped_skus_output.keys()):
                    grouped_skus_output[sku] = grouped_skus_output[sku] + box[box_type][sku]
                else:
                    grouped_skus_output[sku] = box[box_type][sku]
        return grouped_skus_output

    def group_skus_output_pacotes(self, map_output, grouped_skus_output):
        if map_output["pacotes"] != {}:
            for sku in map_output["pacotes"]:
                sku_pacotes = list(grouped_skus_output.keys())
                if sku in sku_pacotes:
                    grouped_skus_output[sku] = grouped_skus_output[sku] + map_output["pacotes"][sku]
                else:
                     grouped_skus_output[sku] = map_output["pacotes"][sku]
        return grouped_skus_output

    def group_skus_output_nao_paletizados(self, map_output, grouped_skus_output):
        if map_output["nao_paletizados"] != [{}]:
            skus_nao_paletizados = map_output["nao_paletizados"][0]
            for sku in skus_nao_paletizados:
                if sku in list(grouped_skus_output.keys()):
                    grouped_skus_output[sku] = grouped_skus_output[sku] + map_output["nao_paletizados"][sku]
                else:
                     grouped_skus_output[sku] = map_output["nao_paletizados"][sku]
        return grouped_skus_output

    def group_skus_output(self, map_output):
        grouped_skus_output = {}
        map_output_caixas = map_output["caixas"]
        grouped_skus_output = self.group_skus_output_caixas(map_output_caixas, grouped_skus_output)
        grouped_skus_output = self.group_skus_output_pacotes(map_output, grouped_skus_output)
        grouped_skus_output = self.group_skus_output_nao_paletizados(map_output, grouped_skus_output)
        return grouped_skus_output

    def skus_quantities_test(self, map_input, map_output):
        grouped_skus_input = self.group_skus_input(map_input)
        grouped_skus_output = self.group_skus_output(map_output)
        message = "First value and second value are not equal !"
        for sku_input in list(grouped_skus_input.keys()):
            sku_output_qt = grouped_skus_output.pop(sku_input)
            self.assertEqual(sku_output_qt, grouped_skus_input[sku_input], message)
        self.assertEqual(grouped_skus_output, {}, message)





       