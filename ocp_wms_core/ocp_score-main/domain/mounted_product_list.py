class MountedProductList:
    """Fluent filtering interface for MountedProduct collections (similar to ItemList).
    
    Provides chainable methods to filter and query mounted products, mimicking C# LINQ patterns.
    All filter methods return a new MountedProductList to enable method chaining.
    """

    def __init__(self, mounted_products):
        self.mounted_products = list(mounted_products) if mounted_products else []

    # --- Type checking methods ---
    def GroupByGroupCode(self):
        """Group mounted products by Product.PackingGroup.GroupCode.

        Returns a GroupedMountedProductList where each group is a MountedProductList.
        """
        groups = {}
        for mp in self.mounted_products:
            try:
                code = mp.Product.PackingGroup.GroupCode
            except Exception:
                code = None
            groups.setdefault(code, []).append(mp)

        grouped = [MountedProductList(lst) for lst in groups.values()]
        return GroupedMountedProductList(grouped)

    GroupByGroupCode = GroupByGroupCode
    def is_chopp(self):
        """Filtra mounted products do tipo Chopp"""
        filtrados = [mp for mp in self.mounted_products if mp.Product.is_chopp()]
        return MountedProductList(filtrados)

    def not_chopp(self):
        """Filtra mounted products que NÃO são do tipo Chopp"""
        filtrados = [mp for mp in self.mounted_products if not mp.Product.is_chopp()]
        return MountedProductList(filtrados)

    def is_returnable(self):
        """Filtra mounted products do tipo Returnable"""
        filtrados = [mp for mp in self.mounted_products if mp.Product.is_returnable()]
        return MountedProductList(filtrados)

    def not_returnable(self):
        """Filtra mounted products que NÃO são do tipo Returnable"""
        filtrados = [mp for mp in self.mounted_products if not mp.Product.is_returnable()]
        return MountedProductList(filtrados)

    def is_isotonic_water(self):
        """Filtra mounted products do tipo IsotonicWater"""
        filtrados = [mp for mp in self.mounted_products if mp.Product.is_isotonic_water()]
        return MountedProductList(filtrados)

    def not_isotonic_water(self):
        """Filtra mounted products que NÃO são do tipo IsotonicWater"""
        filtrados = [mp for mp in self.mounted_products if not mp.Product.is_isotonic_water()]
        return MountedProductList(filtrados)

    def is_package(self):
        """Filtra mounted products do tipo Package"""
        filtrados = [mp for mp in self.mounted_products if mp.Product.is_package()]
        return MountedProductList(filtrados)

    def is_box_template(self):
        """Filtra mounted products do tipo BoxTemplate"""
        filtrados = [mp for mp in self.mounted_products if mp.Product.is_box_template()]
        return MountedProductList(filtrados)

    def not_marketplace(self):
        """Filtra mounted products que NÃO são marketplace (Package ou BoxTemplate)"""
        filtrados = [mp for mp in self.mounted_products if mp.NotMarketplace()]
        return MountedProductList(filtrados)

    # --- Pallet configuration methods ---
    def is_top_of_pallet(self):
        """Filtra mounted products com IncludeTopOfPallet = True"""
        filtrados = [mp for mp in self.mounted_products if mp.Product.PalletSetting.IncludeTopOfPallet]
        return MountedProductList(filtrados)

    def not_top_of_pallet(self):
        """Filtra mounted products com IncludeTopOfPallet = False"""
        filtrados = [mp for mp in self.mounted_products if not mp.Product.PalletSetting.IncludeTopOfPallet]
        return MountedProductList(filtrados)

    def is_base_pallet(self):
        """Filtra mounted products com BasePallet = True"""
        filtrados = [mp for mp in self.mounted_products if mp.Product.PalletSetting.BasePallet]
        return MountedProductList(filtrados)

    def not_base_pallet(self):
        """Filtra mounted products com BasePallet = False"""
        filtrados = [mp for mp in self.mounted_products if not mp.Product.PalletSetting.BasePallet]
        return MountedProductList(filtrados)

    # --- Layer methods ---
    def only_layer(self):
        """Filtra mounted products com LayerCode > 0"""
        filtrados = [mp for mp in self.mounted_products if mp.Product.LayerCode > 0]
        return MountedProductList(filtrados)

    def not_layer(self):
        """Filtra mounted products com LayerCode == 0"""
        filtrados = [mp for mp in self.mounted_products if mp.Product.LayerCode == 0]
        return MountedProductList(filtrados)

    # def not_layer(self):
    #     """Filtra mounted products que NÃO são layer.
    #     Usa Product.PalletSetting (IsLayer / is_layer / Layers) quando disponível; fallback para Product.LayerCode.
    #     Acessa atributos diretamente sem getattr.
    #     """
    #     filtrados = []
    #     for mp in self.mounted_products:
    #         is_layer = False
    #         try:
    #             try:
    #                 # tenta propriedade PascalCase
    #                 is_layer = bool(mp.Product.PalletSetting.IsLayer)
    #             except AttributeError:
    #                 try:
    #                     # tenta propriedade snake_case
    #                     is_layer = bool(mp.Product.PalletSetting.is_layer)
    #                 except AttributeError:
    #                     try:
    #                         # tenta Layers numeric
    #                         is_layer = int(mp.Product.PalletSetting.Layers) > 0
    #                     except Exception:
    #                         is_layer = False
    #         except AttributeError:
    #             try:
    #                 # fallback para Product.LayerCode
    #                 is_layer = int(mp.Product.LayerCode) > 0
    #             except Exception:
    #                 is_layer = False

    #         if not is_layer:
    #             filtrados.append(mp)

    #     return MountedProductList(filtrados)
    
    # --- Assembly sequence methods ---
    def without_assembly_sequence(self):
        """Filtra mounted products com AssemblySequence == 0"""
        filtrados = [mp for mp in self.mounted_products if mp.AssemblySequence == 0]
        return MountedProductList(filtrados)

    # --- Amount methods ---
    def with_amount(self):
        """Filtra mounted products com Amount > 0"""
        filtrados = [mp for mp in self.mounted_products if mp.Amount > 0]
        return MountedProductList(filtrados)

    # --- Ordering methods ---
    def order_by_assembly_sequence(self):
        """Ordena por AssemblySequence ASC"""
        sorted_products = sorted(self.mounted_products, key=lambda x: x.AssemblySequence)
        return MountedProductList(sorted_products)

    def order_by_order_number(self):
        """Ordena por Order.Number (fallback para DeliveryOrder)."""
        def key(x):
            try:
                try:
                    return int(str(x.Order.Number).strip())
                except Exception:
                    return 0
            except Exception as e:
                print(f"Error:: {e}")
                return 0

        sorted_products = sorted(self.mounted_products, key=key)
        return MountedProductList(sorted_products)

    def order_by_group_code(self):
        """Ordena por Product.PackingGroup.GroupCode ASC"""
        sorted_products = sorted(
            self.mounted_products,
            key=lambda x: x.Product.PackingGroup.GroupCode if x.Product.PackingGroup else 0
        )
        return MountedProductList(sorted_products)

    def order_by_desc_is_returnable_and_layers(self):
        """Implements C# OrderByDescIsReturnableAndLayers:
        OrderByDescending(x => !(x.Product is IReturnable))
        .ThenByDescending(p => p.Amount / p.Product.PalletSetting.QuantityBallast)
        """
        def key(x):
            try:
                # primary: !(Product is IReturnable) -> True for non-returnable
                is_returnable = False
                prod = getattr(x, 'Product', None)
                if prod is not None:
                    is_returnable = (prod.is_returnable() if callable(getattr(prod, 'is_returnable', None)) else getattr(prod, 'PalletSetting', None) and False)
                primary = not bool(is_returnable)

                # secondary: Amount / QuantityBallast
                try:
                    qty_ballast = getattr(prod, 'PalletSetting', None)
                    if qty_ballast is not None:
                        q = getattr(qty_ballast, 'QuantityBallast', getattr(qty_ballast, 'quantity_ballast', None))
                        q = float(q) if q not in (None, 0) else 1.0
                    else:
                        q = 1.0
                except Exception:
                    q = 1.0

                amt = float(getattr(x, 'Amount', getattr(x, 'amount', 0)) or 0)
                secondary = amt / q if q != 0 else amt
                return (primary, secondary)
            except Exception as e:
                print(f"Error:: {e}")
                return (False, 0)

        sorted_products = sorted(self.mounted_products, key=key, reverse=True)
        return MountedProductList(sorted_products)

    def order_by_amount_desc(self):
        """Ordena por Amount DESC"""
        sorted_products = sorted(self.mounted_products, key=lambda x: x.Amount, reverse=True)
        return MountedProductList(sorted_products)
    
    def order_by_amount_desc(self):
        """Ordena por Amount DESC"""
        sorted_products = sorted(self.mounted_products, key=lambda x: x.Amount, reverse=True)
        return MountedProductList(sorted_products)
    
    def order_by_package_occupation_desc_then_by_amount_desc(self):
        """Implements C# OrderByPackageOccupationDescThenByAmountDesc semantics.

        - Group by Product.PackingGroup.PackingCode
        - Order groups by sum(PercentOccupationIntoDefaultPalletSize) desc
        - Within each group, group by Product.Code and order those groups by
          sum(PercentOccupationIntoDefaultPalletSize + Occupation) desc,
          then by sum(Amount) desc
        - Flatten and return in that order
        """
        from collections import defaultdict
        # group by packing code
        groups = defaultdict(list)
        for mp in self.mounted_products:
            try:
                packing_group = getattr(mp.Product, 'PackingGroup', None)
                packing_code = getattr(packing_group, 'PackingCode', None) if packing_group is not None else None
            except Exception as e: print(f"Error:: {e}"); packing_code = None
            groups[packing_code].append(mp)

        def sum_percent(group_list):
            total = 0
            for m in group_list:
                try:
                    total += float(getattr(m, 'PercentOccupationIntoDefaultPalletSize', 0) or 0)
                except Exception as e: print(f"Error:: {e}"); total += 0
            return total

        def sum_occ_plus_percent(prod_group):
            total = 0
            for m in prod_group:
                try:
                    p = float(getattr(m, 'PercentOccupationIntoDefaultPalletSize', 0) or 0)
                except Exception as e: print(f"Error:: {e}"); p = 0
                try:
                    o = float(getattr(m, 'Occupation', 0) or 0)
                except Exception as e: print(f"Error:: {e}"); o = 0
                total += (p + o)
            return total

        # order groups by percent desc
        ordered_group_lists = sorted(groups.values(), key=lambda g: sum_percent(g), reverse=True)

        ordered_result = []
        for grp in ordered_group_lists:
            # subgroup by product code
            prod_groups = defaultdict(list)
            for m in grp:
                try:
                    code = getattr(m.Product, 'Code', None)
                except Exception as e: print(f"Error:: {e}"); code = None
                prod_groups[code].append(m)

            # order product groups by (percent+occupation) desc, then by amount desc
            def prod_group_key(pg):
                try:
                    amt_sum = sum(int(x.Amount) for x in pg)
                except Exception as e: print(f"Error:: {e}"); amt_sum = 0
                return (sum_occ_plus_percent(pg), amt_sum)

            ordered_prod_groups = sorted(prod_groups.values(), key=prod_group_key, reverse=True)
            for pg in ordered_prod_groups:
                ordered_result.extend(pg)

        return MountedProductList(ordered_result)

    # --- Generic filtering ---
    def matching(self, predicate):
        """Aplica uma função de filtro genérica"""
        if predicate:
            filtrados = [mp for mp in self.mounted_products if predicate(mp)]
            return MountedProductList(filtrados)
        return self

    def first(self):
        """Retorna o primeiro elemento ou None (First/FirstOrDefault parity)."""
        return self.mounted_products[0] if self.mounted_products else None

    # --- Utility methods ---
    def any(self):
        """Retorna True se houver algum mounted product"""
        return len(self.mounted_products) > 0

    def count(self):
        """Quantidade de mounted products"""
        return len(self.mounted_products)

    def to_list(self):
        """Converte para lista Python nativa"""
        return list(self.mounted_products)

    def __iter__(self):
        """Permite iterar normalmente"""
        return iter(self.mounted_products)

    def __len__(self):
        """Permite usar len()"""
        return len(self.mounted_products)

    def __bool__(self):
        """Permite usar em contextos booleanos"""
        return len(self.mounted_products) > 0

    def __repr__(self):
        return f"<MountedProductList: {len(self.mounted_products)} products>"

    # --- PascalCase aliases for C# compatibility ---
    IsChopp = is_chopp
    NotChopp = not_chopp
    IsReturnable = is_returnable
    NotReturnable = not_returnable
    IsIsotonicWater = is_isotonic_water
    NotIsotonicWater = not_isotonic_water
    IsPackage = is_package
    IsBoxTemplate = is_box_template
    NotMarketplace = not_marketplace
    IsTopOfPallet = is_top_of_pallet
    NotTopOfPallet = not_top_of_pallet
    IsBasePallet = is_base_pallet
    NotBasePallet = not_base_pallet
    OnlyLayer = only_layer
    NotLayer = not_layer
    WithoutAssemblySequence = without_assembly_sequence
    WithAmount = with_amount
    OrderByAssemblySequence = order_by_assembly_sequence
    OrderByGroupCode = order_by_group_code
    OrderByAmountDesc = order_by_amount_desc
    OrderByOrderNumber = order_by_order_number
    OrderByDescIsReturnableAndLayers = order_by_desc_is_returnable_and_layers
    OrderByPackageOccupationDescThenByAmountDesc = order_by_package_occupation_desc_then_by_amount_desc
    Matching = matching
    Any = any
    Count = count
    ToList = to_list
    First = first

class GroupedMountedProductList:
    """Helper wrapper for a collection of MountedProductList groups.

    Provides ordering helpers such as OrderByDescending so call sites like
    `GroupByGroupCode().OrderByDescending(func)` work similarly to LINQ.
    """
    def __init__(self, groups):
        # groups is a list of MountedProductList
        self.groups = list(groups) if groups else []

    def OrderByDescending(self, key_selector):
        try:
            sorted_groups = sorted(self.groups, key=key_selector, reverse=True)
            return GroupedMountedProductList(sorted_groups)
        except Exception:
            return GroupedMountedProductList(self.groups)

    def order_by_descending(self, key_selector):
        return self.OrderByDescending(key_selector)

    # allow iteration
    def __iter__(self):
        return iter(self.groups)

    def __len__(self):
        return len(self.groups)

    def ToList(self):
        return list(self.groups)

    def FirstOrDefault(self):
        return self.groups[0] if self.groups else None


class GroupedMountedProductList:
    """Helper wrapper for a collection of MountedProductList groups.

    Provides ordering helpers such as OrderByDescending so call sites like
    `GroupByGroupCode().OrderByDescending(func)` work similarly to LINQ.
    """
    def __init__(self, groups):
        # groups is a list of MountedProductList
        self.groups = list(groups) if groups else []

    def OrderByDescending(self, key_selector):
        try:
            sorted_groups = sorted(self.groups, key=key_selector, reverse=True)
            return GroupedMountedProductList(sorted_groups)
        except Exception:
            return GroupedMountedProductList(self.groups)

    def order_by_descending(self, key_selector):
        return self.OrderByDescending(key_selector)

    # allow iteration
    def __iter__(self):
        return iter(self.groups)

    def __len__(self):
        return len(self.groups)

    def ToList(self):
        return list(self.groups)

    def FirstOrDefault(self):
        return self.groups[0] if self.groups else None

