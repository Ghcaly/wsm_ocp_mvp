#!/usr/bin/env python3
"""
convert.py - Entry point modular para conversao XML para JSON
"""
import sys
import json
import re
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

# Import modules
from modules import XmlConverter


def main():
    """Entry point para conversao de XML."""
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
    
    args = parser.parse_args()
    
    print(f"\nXML Converter - Processando {Path(args.input).name}...")
    print("=" * 80)
    
    # Initialize converter
    converter = XmlConverter()
    
    try:
        input_path = Path(args.input)
        
        if not input_path.exists():
            print(f"\nErro: '{args.input}' nao encontrado\n")
            return 1
        
        # Build overrides dict
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
        
        # Process directory or single file
        if input_path.is_dir():
            # Process all XML files in directory
            xml_files = list(input_path.glob('*.xml'))
            
            if not xml_files:
                print(f"\nNenhum arquivo XML encontrado em '{args.input}'\n")
                return 1
            
            print(f"\nEncontrados {len(xml_files)} arquivos XML")
            print(f"Diretorio de saida: {args.output}\n")
            
            # Create output directory if needed
            output_dir = Path(args.output)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            success_count = 0
            error_count = 0
            
            for xml_file in xml_files:
                try:
                    print(f"\n{'=' * 80}")
                    print(f"Processando: {xml_file.name}")
                    print(f"{'=' * 80}")
                    
                    # Extract map number from filename (e.g., _m_mapa_163751_ or _e_mapa_163751_)
                    match = re.search(r'_[me]_mapa_(\d+)_', xml_file.name)
                    if match:
                        map_number = match.group(1)
                        output_filename = f"JsonInMapsV2{map_number}.json"
                    else:
                        # Fallback to original name if pattern not found
                        output_filename = f"{xml_file.stem}.json"
                    
                    output_file = output_dir / output_filename
                    
                    # Convert
                    result = converter.convert(str(xml_file), str(output_file), **overrides)
                    
                    # Save to file
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    # Brief summary
                    print(f"Concluido: {result.get('Number')} | "
                          f"{len(result.get('Orders', []))} pedidos | "
                          f"{sum(len(o.get('Items', [])) for o in result.get('Orders', []))} items")
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"Erro ao processar {xml_file.name}: {e}")
                    error_count += 1
            
            # Final summary
            print(f"\n{'=' * 80}")
            print("RESUMO FINAL")
            print(f"{'=' * 80}")
            print(f"Sucesso: {success_count}")
            print(f"Erros: {error_count}")
            print(f"Total: {len(xml_files)}")
            print(f"{'=' * 80}\n")
            
            return 0 if error_count == 0 else 1
        
        else:
            # Single file processing
            # Check if output should use map number pattern
            output_path = Path(args.output)
            if output_path.is_dir():
                # Extract map number from input filename
                match = re.search(r'_[me]_mapa_(\d+)_', input_path.name)
                if match:
                    map_number = match.group(1)
                    output_file = output_path / f"JsonInMapsV2{map_number}.json"
                else:
                    output_file = output_path / f"{input_path.stem}.json"
            else:
                output_file = output_path
            
            print("\nLendo XML...")
            result = converter.convert(args.input, str(output_file), **overrides)
            
            # Save to file
            print("Salvando JSON...")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # Summary
            print("\n" + "=" * 80)
            print("CONVERSAO CONCLUIDA")
            print("=" * 80)
            print(f"  Mapa: {result.get('Number')}")
            print(f"  UnbCode: {result.get('Warehouse', {}).get('UnbCode')}")
            print(f"  Pedidos: {len(result.get('Orders', []))}")
            
            total_items = sum(len(order.get('Items', [])) for order in result.get('Orders', []))
            print(f"  Items: {total_items}")
            
            print(f"\nArquivo gerado: {output_file}")
            print("=" * 80 + "\n")
            
            return 0
        
    except ET.ParseError as e:
        print(f"\nErro ao parsear XML: {e}\n")
        return 1
    except Exception as e:
        print(f"\nErro: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
