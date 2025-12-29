from typing import List, Dict, Tuple, Set, Optional
import numpy as np
import pandas as pd
import copy
import pathlib
import json
import os
import logging
# from ddtrace import patch_all; patch_all(logging=True)


class Utils:


    def __init__(
        self
    ) -> None:

        """
        Common methods used across files 
        """   
    

    def get_filepath(self) -> str:
        return str(pathlib.Path(__file__).parent.resolve())

    def open_json(self, json_file) -> Dict:
        with open(json_file, 'r+') as f:
            file = json.load(f)
        return file

    def write_json(self, json_filename, json_content) -> None:
        with open(json_filename, 'w+') as f:
            f.truncate(0)
            json.dump(json_content, f, sort_keys = True, indent = 4,)

    def refactor_dict(self, dict1):    
        return {k:int(dict1[k]) for k in dict1.keys()}

    def refactor_item_list(self, items, final_list, list_to_add):
        list_quantities_mid = {it:0 for it in items.keys()}

        for fl in final_list.keys():
            list_quantities_mid[fl] = final_list[fl]

        for la in list_to_add.keys():
            list_quantities_mid[la] = list_to_add[la]

        list_quantities = {}

        for lq in list_quantities_mid.keys():
            if list_quantities_mid[lq] > 0:
                list_quantities[lq] = list_quantities_mid[lq] 
        return list_quantities





    

