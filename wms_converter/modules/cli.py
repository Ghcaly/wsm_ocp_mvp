import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Converte XML (ocpEntrega/ocpOrtec) para JSON do sistema'
    )
    parser.add_argument('-i', '--input', required=True, help='Arquivo XML de entrada')
    parser.add_argument('-o', '--output', required=True, help='Arquivo JSON de saída')
    parser.add_argument('--unique-key', help='Force UniqueKey value')
    parser.add_argument('--unbcode', help='Force Warehouse.UnbCode')
    parser.add_argument('--delivery-date', help='Force DeliveryDate (ISO format)')
    parser.add_argument('--plate', help='Force Vehicle.Plate')
    parser.add_argument('--support-point', help='Force Cross.SupportPoint for all orders')
    return parser.parse_args()

def build_overrides(args):
    overrides = {}
    if args.unique_key:
        overrides['unique_key'] = args.unique_key
    if args.unbcode:
        overrides['unbcode'] = args.unbcode
    if args.delivery_date:
        overrides['delivery_date'] = args.delivery_date
    if args.plate:
        overrides['plate'] = args.plate
    if args.support_point:
        overrides['support_point'] = args.support_point
    return overrides
