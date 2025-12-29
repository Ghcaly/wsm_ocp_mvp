from typing import Union
import logging
from .errors import OutputConversionError, UnexpectedType


class OutputConverter:
    """Realiza a conversão do formato de saída da biblioteca para o model usado na aplicação"""

    def _convert_skus(self, data: dict) -> list:
        result = []
        for k, v in data.items():
            result.append({'code': int(k), 'quantity': v})
        return result

    def _convert_item(self, data: dict) -> dict:
        result = {}
        for k, v in data.items():
            result.update({'code': int(k), 'skus': self._convert_skus(v)})
        return result

    def _convert_items(self, name: str, data: Union[list, dict]) -> dict:
        result = []
        if isinstance(data, dict):
            for v in data.values():
                result.append(self._convert_item(v))
        elif isinstance(data, list):
            for i in data:
                result = self._convert_skus(i)
                break
        return {name: result}

    def convert(self, input: dict) -> dict:
        try:
            if not isinstance(input, dict):
                raise UnexpectedType(input, 'dict')
            result = self._convert_items('boxes', input['caixas'])
            result.update({'packages': self._convert_skus(input['pacotes'])})
            result.update(self._convert_items(
                'unboxed_items', input['nao_paletizados']))
            return result
        except Exception as ex:
            err = OutputConversionError(ex)
            logging.exception(err)
            raise err from ex
