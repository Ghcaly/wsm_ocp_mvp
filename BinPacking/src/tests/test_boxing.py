
import json
import pathlib

from boxing.outputToInput import OutputToInput
from boxing.output import Output
from boxing.step import Step
from boxing.input import Input
from boxing.caixaStep import CaixaStep
from boxing.pacoteStep import PacoteStep
from boxing.garrafeiraStep import GarrafeiraStep
from boxing.orders import Orders 
from boxing.boxes import Boxes
from boxing.items import Items
from boxing.utils import Utils
from boxing.packer import BoxerPacker
from boxing.configuration import Configuration
from boxing.unitBoxing import UnitBoxing

from tests.tOrders import TOrders
from tests.tBoxes import TBoxes
from tests.tItems import TItems
from tests.tFakeOutput import TFakeOutput
from tests.tReadFakeInput import TReadFakeInput
from tests.tFakeInput import TFakeInput
from tests.tConfiguration import TConfiguration
from tests.tPacker import TPacker
from tests.tUnitBoxing import TUnitBoxing
from tests.tRealMaps import TRealMaps
from tests.multiple_real_maps import get_res

input_max_weight = '/samples/input_mapa_0_gross_weight.json'
boxes_file = '/samples/boxes_input.json'
items_file = '/samples/items_test.json'
file_skus = '/samples/itens_df2.csv'
result_file = '/samples/result.json'
result_file_erros = '/samples/result_erros.json'
result_file_real = '/samples/result_real.json'
file_map = '/samples/mapa_0.csv'
sample_file = "/samples/input_mapa_0.json"
out_file = "/samples/output_mapa_0.json"
general_test_file = '/samples/input_mapa_0_v2.json'
general_test_file_erros = '/samples/input_mapa_0_com_erros.json'
general_test_file_real = '/samples/input_mapa_real.json'
orders_test_file = '/samples/orders_test.json'
items_sample = '/samples/items_test_sample.json'
items_test_file = '/samples/items_test.json'
config_file = "/samples/parameters_test.json"
map_number = '01234'
name = 'test_map_0'
out_weight = "/samples/out_mapa_0_gross_weight.json"
out_general_file = "/samples/output_mapa_0_geral.json"
out_general_file_packer = "/samples/output_mapa_0_geral_packer.json"
out_real_maps = "/samples/output_mapa_0_geral_packer.json"
out_real_multiple_maps = "/samples/resultados_mapas_reais_total.json"
map_test_families = "/samples/input_mapa_0_v5.json"
map_test_families_result = "/samples/result_families.json"
number_of_boxes = 100
max_wei = 25

utils = Utils()

def input_setup(name,
                input_file,
                map_number,
                number_of_boxes):
    mock_input = TReadFakeInput(
                    name = name, 
                    input_file =  input_file, 
                    map_number = map_number,
                    number_of_boxes = number_of_boxes,
                    max_weight = max_wei)
    input_orders = Orders(input_data = mock_input.map, map_number = map_number)
    algo_boxes = {b:Boxes(box_name = b, input_data = mock_input.boxes[b], map_id = map_number, verbose = True) for b in mock_input.boxes.keys()}
    algo_items = {s:Items(promax_code = s, input_data = mock_input.skus[s], map_id = map_number, verbose = True) for s in mock_input.skus.keys()}
    algo_input = Input('original_input', 
                  orders = input_orders, 
                  skus_info = algo_items, 
                  boxes_info = algo_boxes,
                  number_of_boxes = number_of_boxes,
                  max_weight = max_wei)
    return algo_input

def test_algorithm():
    """A method responsible for executing tests in the boxing library.
    """
    sample_path = str(pathlib.Path(__file__).parent.resolve())
    algo_input = input_setup(name,
                sample_path+ general_test_file,
                map_number,
                number_of_boxes)
    t_input = TFakeInput()
    t_input.t_input_orders(filename = sample_path+sample_file, input = algo_input, input_step = 'orders')
    pacote_step = PacoteStep(verbose = True, map_id = map_number)
    pacote_output = pacote_step.apply(step_input = algo_input)
    t_pacote_output = TFakeOutput()
    t_pacote_output.t_output(filename = sample_path+out_file,
                                        step = "out_PacoteStep",
                                        output = pacote_output,
                                        output_part = 'new_orders')
    garrafeira_input = OutputToInput(
                            name = 'garrafeira_input', 
                            output = pacote_output, 
                            original_input = algo_input,
                            step_name = 'garrafeira',
                            number_of_boxes = number_of_boxes).apply()
    t_input.t_input_orders(filename = sample_path+sample_file, input = garrafeira_input, input_step = 'input_garrafeiraStep')
    garrafeira_step = GarrafeiraStep(verbose = True, map_id = map_number)
    garrafeira_output = garrafeira_step.apply(step_input = garrafeira_input)
    t_garrafeira_output = TFakeOutput()
    t_garrafeira_output.t_output(filename = sample_path+out_file,
                                        step = "out_GarrafeiraStep",
                                        output = garrafeira_output,
                                        output_part = 'new_orders')
    caixa_input = OutputToInput(
                            name = 'caixa_input', 
                            output = garrafeira_output, 
                            original_input = algo_input,
                            step_name = 'caixa',
                            number_of_boxes = number_of_boxes).apply()
    t_input.t_input_orders(
        filename = sample_path+sample_file, 
        input = caixa_input, 
        input_step = 'input_caixaStep')
    caixa_step = CaixaStep(verbose = True, map_id = map_number )
    caixa_output = caixa_step.apply(step_input = caixa_input)
    t_caixa_output = TFakeOutput()
    t_caixa_output.t_output(filename = sample_path+out_file,
                                        step = "out_CaixaStep",
                                        output = caixa_output,
                                        output_part = 'new_orders')

test_algorithm()

def test_algorithm_general_input():
    sample_path = str(pathlib.Path(__file__).parent.resolve())
    with open(sample_path+general_test_file) as json_file:
            data = json.load(json_file)
    input_orders_subdict = data[map_number]
    input_orders = Orders(input_data = input_orders_subdict, map_number = map_number)
    t_orders = TOrders()
    t_orders.t_orders_result(orders_to_test = input_orders.orders_by_invoice, 
                                map_number = input_orders.map, 
                                filename_test = sample_path+orders_test_file)  
    boxes_subdict = data['boxes']
    algo_boxes = [Boxes(box_name = b, input_data = boxes_subdict[b], map_id = map_number, verbose = True) for b in boxes_subdict.keys()]
    t_boxes = TBoxes()
    for b in algo_boxes:
        t_boxes.t_boxes_result(box_obj = b,
                                  box_key = b.box,
                                  filename_test = sample_path + boxes_file)
    with open(sample_path+items_test_file) as json_file:
        items_subdict = json.load(json_file)
    algo_items = {s:Items(promax_code = s, input_data = items_subdict[s], map_id = map_number, verbose = True) for s in items_subdict.keys()}
    t_items = TItems()
    for i in algo_items.keys():
        t_items.t_items_result(item_obj = algo_items[i],
                                  item_key = i,
                                  filename_test = sample_path + items_file,
                                  boxes = algo_boxes)

test_algorithm_general_input()

def test_configuration():
    sample_path = str(pathlib.Path(__file__).parent.resolve())
    data = utils.open_json(sample_path+config_file)
    data_boxes = utils.open_json(sample_path+boxes_file)
    t_configuration = TConfiguration()
    t_configuration.t_parameters(parameters_data = data,
                                    test_filepath = sample_path + '/samples/',
                                    boxes_filetest = data_boxes)  

test_configuration()
    
def test_packer():
    """A method responsible for executing test the boxing library - BoxingPacker class.
    """
    sample_path = str(pathlib.Path(__file__).parent.resolve())
    mock_config = Configuration(filepath = sample_path + '/samples')
    algo_input = input_setup(name,
                sample_path+ general_test_file,
                map_number,
                number_of_boxes)
    boxer_packer = BoxerPacker(general_input = algo_input,
                               config = mock_config,
                               verbose = True, 
                               map_id = map_number)
    result = boxer_packer.apply()
    t_packer_output = TPacker()
    t_packer_output.t_packer_output(filename = sample_path+out_general_file_packer,
                                        output = result[0])

test_packer()

def test_unit_boxing_bt(
        test_file_unit = result_file, 
        data_file = general_test_file,
        flag_families = 1
        ):
    sample_path = str(pathlib.Path(__file__).parent.resolve())
    with open(sample_path+data_file) as json_file:
            data = json.load(json_file)
    algo_box = UnitBoxing(json_input = data,
                          verbose = True)
    algo_result = algo_box.apply()
    t_unt_box = TUnitBoxing()
    t_unt_box.t_unit_boxing(boxing_result = algo_result, test_filepath = sample_path+test_file_unit, flag_families = flag_families)

test_unit_boxing_bt(test_file_unit = result_file, data_file = general_test_file, flag_families = 1)
test_unit_boxing_bt(test_file_unit = result_file_erros, data_file = general_test_file_erros, flag_families = 1)
test_unit_boxing_bt(test_file_unit = result_file_real, data_file = general_test_file_real, flag_families = 1)
test_unit_boxing_bt(test_file_unit = map_test_families_result, data_file = map_test_families, flag_families = 0)



def test_maps_real(data_file = out_real_multiple_maps):
    sample_path = str(pathlib.Path(__file__).parent.resolve())
    with open(sample_path+data_file) as json_file:
            data = json.load(json_file)
    algo_res = get_res()
    t_real_maps = TRealMaps()
    t_real_maps.t_maps(test_res = data, algo_res = algo_res)

test_maps_real()

def test_pacotes_max_weight(test_file_unit = out_weight, 
        data_file = input_max_weight
        ):
    sample_path = str(pathlib.Path(__file__).parent.resolve())
    with open(sample_path+data_file) as json_file:
            data = json.load(json_file)
    algo_box = UnitBoxing(json_input = data,
                          verbose = True)
    algo_result = algo_box.apply()
    t_unt_box = TUnitBoxing()
    t_unt_box.t_unit_boxing(boxing_result = algo_result, test_filepath = sample_path+test_file_unit)

test_pacotes_max_weight()