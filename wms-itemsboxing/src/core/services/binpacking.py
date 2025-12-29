from boxing.unitBoxing import UnitBoxing
from core.converters.input_converter import InputConverter
from core.converters.output_converter import OutputConverter


def get_calculated_boxes(obj: dict) -> dict:
    """Chama a biblioteca para realizar o cálculo"""
    data = InputConverter().convert(obj)
    algo_box = UnitBoxing(json_input=data, verbose=False)
    algo_result = algo_box.apply()
    result = OutputConverter().convert(algo_result)
    return result
