
#     def _safe_sheet_name(self, name: str) -> str:
#         # Excel sheet name limit and invalid chars
#         if not name:
#             return "sheet"
#         safe = ''.join(c for c in name if c not in r'[]:*?/\\')
#         return safe[:31]

#     def _extract_mounted_spaces_data(self, context: Context):
#         data = []
#         for ms in getattr(context, 'MountedSpaces', []) or []:
#             try:
#                 space = getattr(ms, 'Space', ms)
#                 number = getattr(space, 'Number', getattr(space, 'number', None))
#                 side = getattr(space, 'Side', getattr(space, 'side', None))
#                 side_desc = getattr(space, 'SideDesc', getattr(space, 'sideDesc', getattr(space, 'side_desc', None)))
#             except Exception:
#                 number = side = side_desc = None

#             # collect products: prefer ms.get_products(), else iterate containers
#             products = []
#             try:
#                 if hasattr(ms, 'get_products') and callable(ms.get_products):
#                     prods = ms.get_products()
#                 else:
#                     prods = []
#                     for c in getattr(ms, 'Containers', getattr(ms, 'containers', [])) or []:
#                         # container.Products or container.get_products()
#                         if hasattr(c, 'GetProducts') and callable(c.GetProducts):
#                             prods.extend(c.GetProducts())
#                         elif hasattr(c, 'get_products') and callable(c.get_products):
#                             prods.extend(c.get_products())
#                         else:
#                             prods.extend(getattr(c, 'Products', getattr(c, 'products', [])) or [])

#                 for p in prods:
#                     # mounted product wrappers may expose .Item
#                     item = getattr(p, 'Item', None) or getattr(p, 'item', None) or p
#                     code = getattr(item, 'Code', getattr(item, 'code', None))
#                     name = None
#                     prod = getattr(item, 'Product', getattr(item, 'product', None))
#                     if prod is not None:
#                         name = getattr(prod, 'Name', getattr(prod, 'name', None))
#                     qty = getattr(p, 'Amount', getattr(p, 'amount', getattr(item, 'AmountRemaining', getattr(item, 'amount', None))))
#                     products.append({ 'code': code, 'name': name, 'quantity': qty })
#             except Exception:
#                 products = []

#             data.append({ 'space_number': number, 'side': side, 'side_desc': side_desc, 'products': products })
#         return data

#     def _save_mounted_spaces_snapshot(self, context: Context, rule_name: str):
#         """Save mounted spaces snapshot: try .xlsx via openpyxl, fallback to JSON file."""
#         timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
#         reports_dir = Path('reports')
#         reports_dir.mkdir(parents=True, exist_ok=True)
#         data = self._extract_mounted_spaces_data(context)

#         # Try openpyxl and reuse single workbook (add a new sheet per rule)
#         try:
#             from openpyxl import Workbook, load_workbook
#             wb_path = reports_dir / f'mounted_spaces_snapshot.xlsx'
#             if wb_path.exists():
#                 wb = load_workbook(wb_path)
#             else:
#                 wb = Workbook()
#                 # remove default sheet created on new workbook
#                 try:
#                     default = wb.active
#                     wb.remove(default)
#                 except Exception:
#                     pass

#             sheet_base = self._safe_sheet_name(rule_name)
#             sheet_name = self._safe_sheet_name(f"{sheet_base}_{timestamp}")
#             # ensure unique sheet name
#             if sheet_name in wb.sheetnames:
#                 # append a small counter
#                 idx = 1
#                 candidate = sheet_name
#                 while candidate in wb.sheetnames:
#                     candidate = self._safe_sheet_name(f"{sheet_base}_{timestamp}_{idx}")
#                     idx += 1
#                 sheet_name = candidate

#             ws = wb.create_sheet(title=sheet_name)
#             row = 1
#             for entry in data:
#                 ws.cell(row=row, column=1, value='Space Number')
#                 ws.cell(row=row, column=2, value=entry.get('space_number'))
#                 ws.cell(row=row, column=3, value='Side')
#                 ws.cell(row=row, column=4, value=entry.get('side'))
#                 ws.cell(row=row, column=5, value='SideDesc')
#                 ws.cell(row=row, column=6, value=entry.get('side_desc'))
#                 row += 1
#                 # header for products
#                 ws.cell(row=row, column=1, value='Code')
#                 ws.cell(row=row, column=2, value='Name')
#                 ws.cell(row=row, column=3, value='Quantity')
#                 row += 1
#                 for prod in entry.get('products', []):
#                     ws.cell(row=row, column=1, value=prod.get('code'))
#                     ws.cell(row=row, column=2, value=prod.get('name'))
#                     ws.cell(row=row, column=3, value=prod.get('quantity'))
#                     row += 1
#                 # blank row between spaces
#                 row += 1

#             wb.save(wb_path)
#             self.logger.info(f"Snapshot salvo em {wb_path}")
#             return
#         except Exception:
#             # fallback to a single JSON file that accumulates entries
#             json_path = reports_dir / f'mounted_spaces_snapshot.json'
#             try:
#                 existing = []
#                 if json_path.exists():
#                     with open(json_path, 'r', encoding='utf-8') as f:
#                         existing = json.load(f) or []
#                 entry = {'rule': rule_name, 'timestamp': timestamp, 'data': data}
#                 existing.append(entry)
#                 with open(json_path, 'w', encoding='utf-8') as f:
#                     json.dump(existing, f, ensure_ascii=False, indent=2)
#                 self.logger.info(f"Snapshot JSON salvo em {json_path}")
#             except Exception as _je:
#                 self.logger.error(f"Falha ao salvar snapshot JSON fallback: {_je}")
#             return
    
# # try:
# #     self._save_mounted_spaces_snapshot(context, rule_name)
# # except Exception as _ex:
# #     self.logger.error(f"Erro ao salvar snapshot de mounted spaces para {rule_name}: {_ex}")
# # logger.end_step(executed=executed, mounted_spaces=getattr(context, 'MountedSpaces', None))
