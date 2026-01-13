class Output:
    @staticmethod
    def header(filename):
        print(f"\nXML Converter - Processando {filename}...")
    
    @staticmethod
    def file_not_found(path):
        print(f"\nErro: '{path}' nao encontrado\n")
    
    @staticmethod
    def no_xml_files(path):
        print(f"\nNenhum arquivo XML encontrado em '{path}'\n")
    
    @staticmethod
    def batch_start(count, output_dir):
        print(f"\nEncontrados {count} arquivos XML")
        print(f"Diretorio de saida: {output_dir}\n")
    
    @staticmethod
    def processing_file(filename):
        print(f"\nProcessando: {filename}")
    
    @staticmethod
    def file_completed(map_number, order_count, item_count):
        print(f"Concluido: {map_number} | {order_count} pedidos | {item_count} items")
    
    @staticmethod
    def file_error(filename, error):
        print(f"Erro ao processar {filename}: {error}")
    
    @staticmethod
    def batch_summary(success, errors, total):
        print(f"\nRESUMO FINAL")
        print(f"Sucesso: {success}")
        print(f"Erros: {errors}")
        print(f"Total: {total}\n")
    
    @staticmethod
    def reading_xml():
        print("\nLendo XML...")
    
    @staticmethod
    def saving_json():
        print("Salvando JSON...")
    
    @staticmethod
    def conversion_complete(result, output_file):
        print("\nCONVERSAO CONCLUIDA")
        print(f"  Mapa: {result.get('Number')}")
        print(f"  UnbCode: {result.get('Warehouse', {}).get('UnbCode')}")
        print(f"  Pedidos: {len(result.get('Orders', []))}")
        
        total_items = sum(len(order.get('Items', [])) for order in result.get('Orders', []))
        print(f"  Items: {total_items}")
        print(f"\nArquivo gerado: {output_file}\n")
    
    @staticmethod
    def parse_error(error):
        print(f"\nErro ao parsear XML: {error}\n")
    
    @staticmethod
    def generic_error(error):
        print(f"\nErro: {error}\n")
