from domain.space_list import SpaceList
from types import SimpleNamespace
from domain.container_type import ContainerType

class MountedSpaceList:
    """Fluent filtering interface for MountedSpace collections (similar to ItemList).
    
    Provides chainable methods to filter and query mounted spaces, mimicking C# LINQ patterns.
    All filter methods return a new MountedSpaceList to enable method chaining.
    """

    def __init__(self, mounted_spaces):
        self.mounted_spaces = list(mounted_spaces) if mounted_spaces else []

    # --- Space status methods ---
    def has_space_and_not_blocked(self):
        """Filtra mounted spaces que têm espaço disponível e não estão bloqueados"""
        filtrados = [ms for ms in self.mounted_spaces if ms.HasSpaceAndNotBlocked()]
        return MountedSpaceList(filtrados)

    def has_space(self):
        """Filtra mounted spaces que têm espaço disponível"""
        filtrados = [ms for ms in self.mounted_spaces if ms.HasSpace()]
        return MountedSpaceList(filtrados)

    def is_empty(self):
        """Filtra mounted spaces vazios"""
        filtrados = [ms for ms in self.mounted_spaces if ms.IsEmpty()]
        return MountedSpaceList(filtrados)

    def is_occupied(self):
        """Filtra mounted spaces ocupados"""
        filtrados = [ms for ms in self.mounted_spaces if ms.IsOccupied()]
        return MountedSpaceList(filtrados)

    def is_blocked(self):
        """Filtra mounted spaces bloqueados"""
        filtrados = [ms for ms in self.mounted_spaces if ms.IsBlocked()]
        return MountedSpaceList(filtrados)

    def not_blocked(self):
        """Filtra mounted spaces NÃO bloqueados"""
        filtrados = [ms for ms in self.mounted_spaces if not ms.IsBlocked()]
        return MountedSpaceList(filtrados)

    # --- Type checking methods ---
    def is_chopp(self):
        """Filtra mounted spaces do tipo Chopp"""
        filtrados = [ms for ms in self.mounted_spaces if ms.IsChopp()]
        return MountedSpaceList(filtrados)

    def not_chopp(self):
        """Filtra mounted spaces que NÃO são do tipo Chopp"""
        filtrados = [ms for ms in self.mounted_spaces if ms.NotChopp()]
        return MountedSpaceList(filtrados)

    def is_returnable(self):
        """Filtra mounted spaces do tipo Returnable"""
        filtrados = [ms for ms in self.mounted_spaces if ms.IsReturnable()]
        return MountedSpaceList(filtrados)

    def not_returnable(self):
        """Filtra mounted spaces que NÃO são do tipo Returnable"""
        filtrados = [ms for ms in self.mounted_spaces if ms.NotReturnable()]
        return MountedSpaceList(filtrados)

    def is_disposable(self):
        """Filtra mounted spaces do tipo Disposable"""
        filtrados = [ms for ms in self.mounted_spaces if ms.IsDisposable()]
        return MountedSpaceList(filtrados)

    def not_isotonic_water(self):
        """Filtra mounted spaces que NÃO são do tipo IsotonicWater"""
        filtrados = [ms for ms in self.mounted_spaces if ms.NotIsotonicWater()]
        return MountedSpaceList(filtrados)

    # --- Layer methods ---
    def has_layer(self):
        """Filtra mounted spaces que possuem layer"""
        filtrados = [ms for ms in self.mounted_spaces if ms.HasLayer()]
        return MountedSpaceList(filtrados)

    def not_layer(self):
        """Filtra mounted spaces que NÃO possuem layer"""
        filtrados = [ms for ms in self.mounted_spaces if ms.NotLayer()]
        return MountedSpaceList(filtrados)

    # --- Keg exclusive methods ---
    def not_keg_exclusive(self):
        """Filtra mounted spaces que NÃO são keg exclusive"""
        filtrados = [ms for ms in self.mounted_spaces if ms.NotKegExclusive()]
        return MountedSpaceList(filtrados)

    # --- Remount methods ---
    def is_remount(self):
        """Filtra mounted spaces que são remount"""
        filtrados = [ms for ms in self.mounted_spaces if ms.IsRemount()]
        return MountedSpaceList(filtrados)

    def not_remount(self):
        """Filtra mounted spaces que NÃO são remount"""
        filtrados = [ms for ms in self.mounted_spaces if not ms.IsRemount()]
        return MountedSpaceList(filtrados)

    def is_splitted(self):
        """Filtra mounted spaces que têm produtos splitados"""
        filtrados = [ms for ms in self.mounted_spaces if ms.IsSplitted()]
        return MountedSpaceList(filtrados)

    def NotBulk(self):
        """Return mounted spaces that are NOT bulk.

        Determine bulk by inspecting containers on the mounted space: a mounted space
        is considered bulk if any of its containers/pallets has Bulk/bulk == True or
        its ProductBase indicates bulk. This mirrors the C# behavior where Bulk is
        a property of the container/pallet.
        """
        try:
            def _is_bulk(ms):
                try:
                    containers = getattr(ms, "Containers", getattr(ms, "containers", [])) or []
                    for c in containers:
                        if getattr(c, "Bulk", getattr(c, "bulk", False)):
                            return True
                        pb = getattr(c, "ProductBase", getattr(c, "product_base", None))
                        if pb is not None:
                            if getattr(pb, "IsBulk", getattr(pb, "is_bulk", False)) or getattr(pb, "bulk", False):
                                return True
                    return False
                except Exception:
                    return False

            filtrados = [m for m in self.mounted_spaces if not _is_bulk(m)]
            return MountedSpaceList(filtrados)
        except Exception as e:
            print(f"Error:: {e}")
            return MountedSpaceList([])

    def NotContainProductComplex(self):
        """Return mounted spaces that do NOT contain any product marked as ComplexLoad.

        Mirrors C#: mountedSpaces.Where(x => x.GetProducts().All(x => !x.ComplexLoad))
        """
        try:
            def _products_of(ms):
                # prefer method GetProducts(), fallback to get_products()
                gp = getattr(ms, 'GetProducts', None)
                if callable(gp):
                    try:
                        return gp()
                    except Exception:
                        pass
                gp2 = getattr(ms, 'get_products', None)
                if callable(gp2):
                    try:
                        return gp2()
                    except Exception:
                        pass
                # last resort: inspect containers
                try:
                    prods = []
                    for c in getattr(ms, 'Containers', getattr(ms, 'containers', [])) or []:
                        prods.extend(getattr(c, 'Products', getattr(c, 'products', [])) or [])
                    return prods
                except Exception:
                    return []

            filtrados = []
            for ms in self.mounted_spaces:
                products = _products_of(ms) or []
                try:
                    has_complex = any(getattr(p, 'ComplexLoad', getattr(p, 'complex_load', False)) for p in products)
                except Exception:
                    has_complex = False
                if not has_complex:
                    filtrados.append(ms)

            return MountedSpaceList(filtrados)
        except Exception as e:
            print(f"Error:: NotContainProductComplex: {e}")
            return MountedSpaceList([])

    def OrderByOccupation(self):
        """Order mounted spaces by their Occupation (ascending).

        Uses `Occupation` or fallback `occupation` attribute when present.
        Returns a new MountedSpaceList sorted by occupation value.
        """
        try:
            return MountedSpaceList(sorted(self.mounted_spaces, key=lambda ms: float(getattr(ms, 'Occupation', getattr(ms, 'occupation', 0)) or 0)))
        except Exception:
            return MountedSpaceList(self.mounted_spaces)

    def OrderByOccupationDesc(self):
        """Order mounted spaces by their Occupation (descending).

        Uses `Occupation` or fallback `occupation` attribute when present.
        Returns a new MountedSpaceList sorted by occupation value in descending order.
        """
        try:
            return MountedSpaceList(sorted(self.mounted_spaces, key=lambda ms: float(getattr(ms, 'Occupation', getattr(ms, 'occupation', 0)) or 0), reverse=True))
        except Exception:
            return MountedSpaceList(self.mounted_spaces)

    def GetDisposableOrReturnableType(self):
        """
        Return flattened list of containers from mounted spaces that are disposable or returnable.
        Prefer container.get_disposable_or_returnable_type() when available (parity with C# helper).
        """
        containers = []
        for ms in self.mounted_spaces:
            for c in getattr(ms, "Containers", getattr(ms, "containers", [])) or []:
                try:
                    ct = c.get_disposable_or_returnable_type()
                except Exception:
                    # fallback to container helpers if get_disposable_or_returnable_type isn't present
                    try:
                        if callable(getattr(c, "IsTypeBaseWaterIsotonic", None)) and c.IsTypeBaseWaterIsotonic():
                            containers.append(c)
                            continue
                        if callable(getattr(c, "IsTypeBaseReturnable", None)) and not c.IsTypeBaseReturnable():
                            containers.append(c)
                            continue
                    except Exception:
                        pass

                    # final fallback: inspect ProductBase.ContainerType/name/value
                    try:
                        pb = getattr(c, "ProductBase", None)
                        if pb is None:
                            continue
                        ct_fallback = getattr(pb, "ContainerType", getattr(pb, "container_type", None))
                        name = getattr(ct_fallback, "name", None) or str(ct_fallback)
                        if name.upper() in ("DISPOSABLE", "RETURNABLE"):
                            containers.append(c)
                    except Exception:
                        continue
                else:
                    if ct in (ContainerType.DISPOSABLE, ContainerType.RETURNABLE):
                        containers.append(c)

        return containers
    
    def order_by_different_packing_code_quantity_desc_and_product_quantity_desc_and_occupation_desc(self):
        return sorted(
            (ms for ms in self.mounted_spaces if ms.get_products()),
            key=lambda x: (
                -x.get_first_pallet().DifferentPackingGroupQuantity,
                -len(x.get_first_pallet().products),
                -x.occupation
            )
        )

    # def order_by_different_packing_code_quantity_desc_and_product_quantity_desc_and_occupation_desc(
    #     self,
    #     space_size=None,
    #     occupation_calc: callable = None
    # ):
    #     """
    #     Ordena a lista retornando uma nova lista:
    #     1) número de packing codes distintos (desc)
    #     2) soma das quantidades dos produtos (desc)
    #     3) ocupação (desc)

    #     Parâmetros:
    #     - space_size: opcional, usado por occupation_calc ou para buscar occupation_by_space_size nos products.
    #     - occupation_calc: função opcional (mounted_space, space_size) -> numeric para calcular ocupação.
    #     """
    #     def key_for(mounted_space):
    #         # tenta extrair produtos da primeira palete / estrutura compatível
    #         products = []
    #         try:
    #             first_pallet = mounted_space.get_first_pallet()
    #             products = getattr(first_pallet, 'products', []) or []
    #         except Exception:
    #             products = getattr(mounted_space, 'products', []) or []

    #         # packing codes distintos
    #         packing_codes = {
    #             getattr(p.product.PackingGroup, 'packing_code', None)
    #             for p in products
    #         }
    #         distinct_packing_codes = len([pc for pc in packing_codes if pc is not None])

    #         # soma das quantidades dos produtos
    #         product_quantity = sum(
    #             getattr(p, 'amount', getattr(p, 'Amount', 0)) for p in products
    #         )

    #         # ocupação: usa occupation_calc se fornecido, senão tenta heurísticas
    #         if occupation_calc is not None:
    #             occupation = occupation_calc(mounted_space, space_size)
    #         else:
    #             # 1) se mounted_space tem atributo 'occupation' usa ele
    #             occupation_attr = getattr(mounted_space, 'occupation', None)
    #             if occupation_attr is not None:
    #                 occupation = occupation_attr
    #             else:
    #                 # 2) tenta somar occupation_by_space_size dos products (quando disponível)
    #                 if space_size is not None and products:
    #                     occ_sum = 0
    #                     for p in products:
    #                         occ_by_size = getattr(p, 'occupation_by_space_size', None)
    #                         if isinstance(occ_by_size, dict):
    #                             occ_sum += occ_by_size.get(space_size, 0)
    #                         else:
    #                             occ_sum += getattr(p, 'occupation', 0)
    #                     occupation = occ_sum
    #                 else:
    #                     # fallback
    #                     occupation = sum(getattr(p, 'occupation', 0) for p in products)

    #         # retorno invertido para ordenar desc com sorted(..., key=...)
    #         return (-distinct_packing_codes, -product_quantity, -occupation)

    #     return sorted(self, key=key_for)
    
    # --- Side methods ---
    def driver_side(self):
        """Filtra mounted spaces no lado do motorista (Driver Side)"""
        filtrados = [ms for ms in self.mounted_spaces if ms.Space.IsDriverSide()]
        return MountedSpaceList(filtrados)

    def helper_side(self):
        """Filtra mounted spaces no lado do ajudante (Helper Side)"""
        filtrados = [ms for ms in self.mounted_spaces if ms.Space.IsHelperSide()]
        return MountedSpaceList(filtrados)

    # --- Generic filtering ---
    def matching(self, predicate):
        """Aplica uma função de filtro genérica"""
        if predicate:
            filtrados = [ms for ms in self.mounted_spaces if predicate(ms)]
            return MountedSpaceList(filtrados)
        return self

    def NotFull(self):
        """Return mounted spaces that are not full (C#: .Where(x => !x.Full))."""
        return MountedSpaceList([ms for ms in self if not ms.Full])

    def Full(self):
        """Return mounted spaces that are full (C#: .Where(x => x.Full))."""
        return MountedSpaceList([ms for ms in self if ms.Full])

    # --- Utility methods ---
    def any(self):
        """Retorna True se houver algum mounted space"""
        return len(self.mounted_spaces) > 0

    def count(self):
        """Quantidade de mounted spaces"""
        return len(self.mounted_spaces)

    def to_list(self):
        """Converte para lista Python nativa"""
        return list(self.mounted_spaces)

    def __iter__(self):
        """Permite iterar normalmente"""
        return iter(self.mounted_spaces)

    def __len__(self):
        """Permite usar len()"""
        return len(self.mounted_spaces)

    def __getitem__(self, index):
        """Support indexing and slicing. Returns a single mounted space for int
        index or a new MountedSpaceList for slices to mimic list behavior.
        """
        try:
            if isinstance(index, slice):
                return MountedSpaceList(self.mounted_spaces[index])
            return self.mounted_spaces[index]
        except Exception:
            raise

    def __bool__(self):
        """Permite usar em contextos booleanos (if mounted_spaces_list:)"""
        return len(self.mounted_spaces) > 0

    def __repr__(self):
        return f"<MountedSpaceList: {len(self.mounted_spaces)} mounted spaces>"

    # --- PascalCase aliases for C# compatibility ---
    not_full = NotFull
    full = Full
    HasSpaceAndNotBlocked = has_space_and_not_blocked
    HasSpace = has_space
    IsEmpty = is_empty
    IsOccupied = is_occupied
    IsBlocked = is_blocked
    NotBlocked = not_blocked
    IsChopp = is_chopp
    NotChopp = not_chopp
    IsReturnable = is_returnable
    NotReturnable = not_returnable
    IsDisposable = is_disposable
    NotIsotonicWater = not_isotonic_water
    HasLayer = has_layer
    NotLayer = not_layer
    NotKegExclusive = not_keg_exclusive
    IsRemount = is_remount
    NotRemount = not_remount
    IsSplitted = is_splitted
    NotBulk = NotBulk
    OrderByOccupation = OrderByOccupation
    DriverSide = driver_side
    HelperSide = helper_side
    Matching = matching
    Any = any
    Count = count
    ToList = to_list
    
    # --- Spaces extraction and list helpers ---
    def get_spaces(self):
        """Return a SpaceList with the `Space` objects from the mounted spaces."""
        spaces = []
        for ms in self.mounted_spaces:
            s = getattr(ms, 'Space', None)
            if s is None:
                s = getattr(ms, 'space', None)
            if s is not None:
                spaces.append(s)
        return SpaceList(spaces)

    def get_mounted_space(self, space):
        """Return the MountedSpace object that corresponds to `space`.

        `space` may be:
        - a Space object (matching by identity or by Number),
        - an integer or string with space number.

        Returns the matching mounted space or `None` if not found.
        """
        if space is None:
            return None

        # If caller passed a mounted-space instance, return it if present
        try:
            for ms in self.mounted_spaces:
                if space is ms:
                    return ms
        except Exception:
            pass

        # If passed a numeric/string identifier, try to match by Number
        target_num = None
        try:
            if isinstance(space, (int,)):
                target_num = int(space)
            else:
                sp = getattr(space, 'Space', None) or space
                num = getattr(sp, 'Number', getattr(sp, 'number', None))
                if num is not None:
                    target_num = int(str(num).strip())
        except Exception:
            target_num = None

        if target_num is not None:
            for ms in self.mounted_spaces:
                try:
                    ms_sp = getattr(ms, 'Space', None) or getattr(ms, 'space', None) or ms
                    ms_num = getattr(ms_sp, 'Number', getattr(ms_sp, 'number', None))
                    if ms_num is None:
                        continue
                    if int(str(ms_num).strip()) == target_num:
                        return ms
                except Exception:
                    continue

        # Fallback: try matching by Space object equality
        try:
            for ms in self.mounted_spaces:
                ms_sp = getattr(ms, 'Space', None) or getattr(ms, 'space', None)
                if ms_sp is not None and (ms_sp is space or ms_sp == space):
                    return ms
        except Exception:
            pass

        return None

    # PascalCase alias for compatibility
    GetMountedSpace = get_mounted_space

    def OrderByWeightDesc(self):
        """Order mounted spaces by weight descending (heaviest first)."""
        def weight_of(ms):
            try:
                return float(getattr(ms, "Weight", getattr(ms, "weight", 0)) or 0.0)
            except Exception as e: print(f"Error:: {e}"); return 0.0
        try:
            return MountedSpaceList(sorted(self.mounted_spaces, key=weight_of, reverse=True))
        except Exception as e: print(f"Error:: {e}"); return MountedSpaceList(self.mounted_spaces)
        
    order_by_weight_desc = OrderByWeightDesc

    GetSpaces = get_spaces

    def getSpaceByNumber(self, number: Any):
        """Return first space whose Number equals `number` (number may be int/str)."""
        try:
            target = int(str(number).strip())
        except Exception as e: print(f"Error:: {e}"); return None

        for ms in self:
            sp = getattr(ms, "Space", ms)
            sp_num = getattr(sp, "Number", getattr(sp, "number", None))
            try:
                sp_num_int = int(str(sp_num).strip())
            except Exception as e: print(f"Error:: {e}"); continue
            if sp_num_int == target:
                return sp
        return None

    # aliases
    get_space_by_number = getSpaceByNumber
    
    def ordered_by_different_packing_group_quantity_desc_and_occupation(self):
        """Order mounted spaces by sum(cont.DifferentPackingGroupQuantity) desc, then by Occupation asc.

        Mirrors C# OrderByDifferentPackingGroupQuantityDescAndOccupation extension.
        Returns a new MountedSpaceList for chaining.
        """
        try:
            def key_fn(ms):
                try:
                    containers = getattr(ms, 'Containers', []) or []
                    sum_groups = 0
                    for c in containers:
                        sum_groups += int(getattr(c, 'DifferentPackingGroupQuantity', 0))
                    # invert sum for descending primary sort
                    occupation = getattr(ms, 'Occupation', getattr(ms, 'occupation', 0))
                    return (-sum_groups, occupation)
                except Exception as e: print(f"Error:: {e}"); return (0, getattr(ms, 'Occupation', getattr(ms, 'occupation', 0)))

            sorted_ms = sorted(list(self.mounted_spaces), key=key_fn)
            return MountedSpaceList(sorted_ms)
        except Exception as e: print(f"Error:: {e}"); return MountedSpaceList(self.mounted_spaces)

    def OrderByLayerRemountDescAndOccupation(self):
        def key(ms):
            return (ms.HasLayer(),  ms.IsRemount(), ms.Occupation)
        return MountedSpaceList(sorted(self, key=key))

    def OrderByNotRemountDescAndOccupation(self):
        # not remount (i.e. IsRemount == False) first, then occupation ascending
        def key(ms):
            return (not ms.IsRemount(), ms.Occupation)
        return MountedSpaceList(sorted(self, key=key))

    def OrderByRemountDescAndOccupation(self):
        """
        Orders mounted spaces:
        - Remount = True first (descending)
        - then by occupation ascending.

        Mirrors exactly the C# logic:
        OrderByDescending(Remount).ThenBy(Occupation)
        """

        def key(ms):
            occupation = float(ms.Occupation)
            return (not ms.IsRemount(), occupation)  # DESC for remount, ASC for occupation

        ordered = MountedSpaceList(sorted(self, key=key))

        return ordered

    def Difference(self, container, product):
        return abs(container.GroupAndSubGroup - product.GroupAndSubGroup)

    def OrderByLayerAndDifference(self, product):
        # layer True first, then difference (see comment), then occupation asc
        def difference(ms):
            try:
                size = ms.Space.size
                factor = product.GetFactor(size)
                occ = ms.Occupation
                return abs(float(occ) - float(factor.Quantity))
            except Exception as e: print(f"Error:: {e}"); return float("inf")

        def key(ms):
            # return (ms.HasLayer(), self.Difference(ms.get_first_pallet(), product), ms.Occupation)#temporario
            return (ms.HasLayer(), self.Difference(ms.get_first_pallet(), product))
        
        return MountedSpaceList(sorted(self, key=key))

    def OrderByLayerAndDifferenceAndOccupation(self, product):
        """Order by: has layer (True first), difference between occupation and product factor qty (asc), then occupation (asc).

        Mirrors C# OrderByLayerAndDifferenceAndOccupation used when selecting candidate spaces.
        """
        def factor_quantity_for(ms):

            factor = product.GetFactor(ms.Space.Size)
            
            if factor is None:
                return None
            return factor.Quantity

        def difference(ms):
            try:
                occ = float(ms.Occupation)
            except Exception:
                occ = 0.0
            qty = factor_quantity_for(ms)

            if qty is None:
                return float('inf')
            
            try:
                return abs(occ - float(qty))
            except Exception:
                return float('inf')

        def key(ms):
            has_layer = bool(ms.HasLayer())
            try:
                occ = float(ms.Occupation)
            except Exception:
                occ = 0.0
            return (0 if has_layer else 1, self.Difference(ms.get_first_pallet(), product), occ)

        return MountedSpaceList(sorted(self, key=key))

    def OrderByDifferenceAndOccupation(self, product):
        def key(ms):
            try:
                occ = float(ms.Occupation)
            except Exception:
                occ = 0.0
            return (self.Difference(ms.get_first_pallet(), product), occ)
        return MountedSpaceList(sorted(self, key=key))
    
    # def OrderByLayerAndOccupation(self):
    #     # layer True first, then occupation ascending
    #     def key(ms):
    #         has_layer = bool(getattr(ms, "HasLayer", lambda: False)())
    #         occ = float(getattr(ms, "Occupation", getattr(ms, "occupation", 0)) or 0)
    #         return (has_layer, occ)
    #     return MountedSpaceList(sorted(self, key=key))
    
    def OrderByLayerAndOccupation(self):
        # layer False first (same as C#), then occupation ascending
        def key(ms):
            has_layer = bool(ms.HasLayer())
            occ = float(ms.Occupation or 0)
            return (has_layer, occ)

        return MountedSpaceList(sorted(self, key=key))

    def WithOccupationLessThan(self, percent: float):
        """Filter mounted spaces whose occupied percentage is less than `percent`."""
        def occupied_pct(ms):
            try:
                occ = float(ms.Occupation)
                capacity = float(ms.Space.Size)
                return (occ / capacity) * 100 if capacity != 0 else 0.0
            except Exception:
                return 0.0

        filtrados = [ms for ms in self.mounted_spaces if occupied_pct(ms) < float(percent)]
        return MountedSpaceList(filtrados)

    def OrderByOccupiedPercentage(self):
        """Order mounted spaces by occupied percentage ascending."""
        def pct(ms):
            occ = float(ms.Occupation)
            cap = float(ms.Space.Size)
            return (occ / cap) * 100 if cap != 0 else float('inf')

        return MountedSpaceList(sorted(self.mounted_spaces, key=pct))
    
    def WithProducts(self):
        """Return mounted spaces that have at least one product in their containers."""
        filtrados = [ms for ms in self.mounted_spaces if any(len(c.products) > 0 for c in ms.containers)]
        return MountedSpaceList(filtrados)

    def with_products(self):
        return self.WithProducts()

    def WithMinimumQuantityOfItems(self, minimum_quantity: int):
        """Filter mounted spaces where all containers have at least minimum_quantity distinct products (by CodePromax).
        
        C#: mountedSpaces.Where(x => x.Containers.All(y => y.Products.Select(z => z.Product.CodePromax).Count() >= minimumQuantityOfItems))
        """
        def has_minimum(ms):
            containers = getattr(ms, 'Containers', getattr(ms, 'containers', []))
            if not containers:
                return False
            
            # All containers must have >= minimum_quantity distinct products
            for c in containers:
                products = getattr(c, 'Products', getattr(c, 'products', []))
                distinct_codes = set()
                for p in products:
                    prod = getattr(p, 'Product', getattr(p, 'product', None))
                    if prod:
                        code = getattr(prod, 'CodePromax', None)
                        if code:
                            distinct_codes.add(code)
                
                if len(distinct_codes) < minimum_quantity:
                    return False
            
            return True
        
        filtrados = [ms for ms in self.mounted_spaces if has_minimum(ms)]
        return MountedSpaceList(filtrados)

    def with_minimum_quantity_of_items(self, minimum_quantity: int):
        return self.WithMinimumQuantityOfItems(minimum_quantity)
    
    def FilterByGroupCode(self, product):
        """
        Filter mounted spaces where at least one container has all products with the same GroupCode as the given product.
        C#: mountedSpaces.Where(p => p.Containers.Any(x => x.Products.All(r => r.Product.PackingGroup.GroupCode == product.PackingGroup.GroupCode)))
        """
        def matches(ms):
            target_group_code = product.PackingGroup.GroupCode
            # Check if any container has all products with the same GroupCode
            for container in ms.Containers:
                products = container.Products
                if not products:  # Empty container doesn't match
                    continue
                # All products in this container must have the same GroupCode
                if all(mp.Product.PackingGroup.GroupCode == target_group_code for mp in products):
                    return True
            return False
        
        filtrados = [ms for ms in self.mounted_spaces if matches(ms)]
        return MountedSpaceList(filtrados)
    
    def filter_by_group_code(self, product):
        return self.FilterByGroupCode(product)

    def WithMultipleGroups(self):
        """Return mounted spaces where containers contain products from more than one PackingGroup.GroupCode."""
        filtrados = []
        for ms in self.mounted_spaces:
            try:
                containers = getattr(ms, 'Containers', getattr(ms, 'containers', [])) or []
                ok = True
                for c in containers:
                    products = getattr(c, 'Products', getattr(c, 'products', [])) or []
                    group_codes = set()
                    for p in products:
                        prod = getattr(p, 'Product', getattr(p, 'product', None))
                        if not prod:
                            continue
                        pg = getattr(prod, 'PackingGroup', getattr(prod, 'packing_group', None))
                        if not pg:
                            continue
                        code = getattr(pg, 'GroupCode', getattr(pg, 'group_code', None))
                        if code is not None:
                            group_codes.add(code)
                    if len(group_codes) <= 1:
                        ok = False
                        break
                if ok:
                    filtrados.append(ms)
            except Exception:
                continue
        return MountedSpaceList(filtrados)

    def WithSameGroupAndMultiplePackages(self):
        """Return mounted spaces where containers have same group and more than one PackingCode."""
        filtrados = []
        for ms in self.mounted_spaces:
            try:
                containers = getattr(ms, 'Containers', getattr(ms, 'containers', [])) or []
                ok = True
                for c in containers:
                    products = getattr(c, 'Products', getattr(c, 'products', [])) or []
                    group_codes = set()
                    packing_codes = set()
                    for p in products:
                        prod = getattr(p, 'Product', getattr(p, 'product', None))
                        if not prod:
                            continue
                        pg = getattr(prod, 'PackingGroup', getattr(prod, 'packing_group', None))
                        if pg is not None:
                            gc = getattr(pg, 'GroupCode', getattr(pg, 'group_code', None))
                            if gc is not None:
                                group_codes.add(gc)
                            pc = getattr(pg, 'PackingCode', getattr(pg, 'packing_code', None))
                            if pc is not None:
                                packing_codes.add(pc)
                        else:
                            # try fallback to attributes on product
                            gc = getattr(prod, 'GroupCode', getattr(prod, 'group_code', None))
                            if gc is not None:
                                group_codes.add(gc)
                            pc = getattr(prod, 'PackingCode', getattr(prod, 'packing_code', None))
                            if pc is not None:
                                packing_codes.add(pc)

                    if not (len(group_codes) == 1 and len(packing_codes) > 1):
                        ok = False
                        break
                if ok:
                    filtrados.append(ms)
            except Exception:
                continue
        return MountedSpaceList(filtrados)

    def WithSameGroupAndPackageAndMultipleItems(self):
        """Return mounted spaces where containers have same group, same package, and >1 distinct product codes."""
        filtrados = []
        for ms in self.mounted_spaces:
            try:
                containers = getattr(ms, 'Containers', getattr(ms, 'containers', [])) or []
                ok = True
                for c in containers:
                    products = getattr(c, 'Products', getattr(c, 'products', [])) or []
                    group_codes = set()
                    packing_codes = set()
                    product_codes = set()
                    for p in products:
                        prod = getattr(p, 'Product', getattr(p, 'product', None))
                        if not prod:
                            continue
                        pg = getattr(prod, 'PackingGroup', getattr(prod, 'packing_group', None))
                        if pg is not None:
                            gc = getattr(pg, 'GroupCode', getattr(pg, 'group_code', None))
                            if gc is not None:
                                group_codes.add(gc)
                            pc = getattr(pg, 'PackingCode', getattr(pg, 'packing_code', None))
                            if pc is not None:
                                packing_codes.add(pc)
                        else:
                            gc = getattr(prod, 'GroupCode', getattr(prod, 'group_code', None))
                            if gc is not None:
                                group_codes.add(gc)
                            pc = getattr(prod, 'PackingCode', getattr(prod, 'packing_code', None))
                            if pc is not None:
                                packing_codes.add(pc)

                        code = getattr(prod, 'Code', getattr(prod, 'code', None))
                        if code is not None:
                            product_codes.add(code)

                    if not (len(group_codes) == 1 and len(packing_codes) == 1 and len(product_codes) > 1):
                        ok = False
                        break
                if ok:
                    filtrados.append(ms)
            except Exception:
                continue
        return MountedSpaceList(filtrados)
    
    def FilterByGroupCodeAny(self, product):
        target_group_code = product.PackingGroup.GroupCode

        filtrados = [
            ms for ms in self.mounted_spaces
            if any(
                mp.Product.PackingGroup.GroupCode == target_group_code
                for container in ms.Containers
                for mp in container.Products
            )
        ]

        return MountedSpaceList(filtrados)

    def OrderByLayerOccupationAndDifference(self, product):
        """
        Order by: has layer (True first), occupation (asc), difference between occupation and product factor qty (asc).
        Mirrors C# intent used by IsotonicWaterRule when selecting candidate spaces.
        """
        def factor_quantity_for(ms):
            factor = product.GetFactor(ms.Space.Size)
            if factor is None:
                return None
            return float(factor.Quantity or 0)

        def key(ms):
            occ = float(ms.Occupation)
            qty = factor_quantity_for(ms)
            diff = abs(float(occ) - float(qty))
            return (ms.HasLayer(), occ, self.Difference(ms.get_first_pallet(), product))

        for t_ in self:
            print(f"Debug:: MS: {t_.Space.Number} - {t_.Space.sideDesc} MountedSpace {t_.Space.Number} Occupation: {t_.Occupation}, ordernacao {key(t_)}")

        return MountedSpaceList(sorted(self, key=key))
    
    def MaxTwoSpacesOfDistanceTo(self, target_space):
        """
        Return up to two spaces from this list that are the closest to target_space
        and at distance <= 2 (by space.Number). Mirrors C# MaxTwoSpacesOfDistanceTo.
        """
        def unwrap_space(s):
            # s may be a Space or a DTO with .Space
            return getattr(s, "Space", s)

        def num_of(s):
            sp = unwrap_space(s)
            n = getattr(sp, "Number", None)
            if n is None:
                n = getattr(sp, "number", None)
            try:
                return int(n)
            except Exception:
                return None

        target_num = num_of(target_space)
        if target_num is None:
            return MountedSpaceList([])

        candidates = []
        for s in self:
            n = num_of(s)
            if n is None:
                continue
            dist = abs(n - target_num)
            if dist == 0:
                continue
            if dist <= 2:
                candidates.append((dist, n, unwrap_space(s)))

        # sort by distance asc then by number asc, return up to two space objects
        candidates.sort(key=lambda t: (t[0], t[1]))
        return MountedSpaceList([c[2] for c in candidates[:2]])

    # snake_case alias
    max_two_spaces_of_distance_to = MaxTwoSpacesOfDistanceTo

    def WhereIsNot(self, mounted_space):
        """Return list excluding a mounted space or a collection of mounted spaces."""
        if isinstance(mounted_space, (list, tuple, set)):
            exclude = set(mounted_space)
            return MountedSpaceList([ms for ms in self if ms not in exclude])
        return MountedSpaceList([ms for ms in self if ms is not mounted_space and ms != mounted_space])

    def WithSameTypes(self, *container_types):
        """
        Filter mounted spaces that have at least one container whose 
        ProductBase.ContainerType matches ANY of container_types.

        container_types may be:
            - one or more types
            - a callable predicate(ms) -> bool
        """

        # Se for passado um único argumento e ele for um callable → use como predicate
        if len(container_types) == 1 and callable(container_types[0]):
            predicate = container_types[0]
            return MountedSpaceList([ms for ms in self if predicate(ms)])

        # Normaliza tipos em um set para comparação eficiente
        valid_types = set(container_types)

        def matches(ms):
            pallet = ms.get_first_pallet()
            if not pallet:
                return False
            return pallet.ProductBase.ContainerType in valid_types

        return MountedSpaceList([ms for ms in self if matches(ms)])

    def WithSameType(self, container_type):
        """
        Filter mounted spaces that have at least one container whose ProductBase.ContainerType == container_type.
        If container_type is a callable, treat it as a predicate(ms) -> bool.
        """
        if callable(container_type):
            return MountedSpaceList([ms for ms in self if container_type(ms)])

        def has_type(ms):
            for c in getattr(ms, "Containers", []):
                pb = getattr(c, "ProductBase", None)
                if pb is None:
                    continue
                if getattr(pb, "ContainerType", None) == container_type:
                    return True
            return False

        def type(ms):
            if not ms.get_first_pallet():
                return False
            return ms.get_first_pallet().ProductBase.ContainerType == container_type
        return MountedSpaceList([ms for ms in self if type(ms)])

    def ordered_by_descending(self, key_selector):
        """
        Return a MountedSpaceList ordered by key_selector in descending order.
        Usage: MountedSpaceList(...).ordered_by_descending(lambda s: s.occupation_remaining)
        """
        try:
            return MountedSpaceList(sorted(self.mounted_spaces, key=key_selector, reverse=True))
        except Exception as e:
            print(f"Error:: {e}")
            # fallback: return unchanged list wrapped
            return MountedSpaceList(self.mounted_spaces)

    # PascalCase / alternative aliases
    OrderByDescending = ordered_by_descending
    order_by_descending = ordered_by_descending

    def FirstOrDefault(self, predicate=None):
        """
        Return the first element that matches predicate or the first element if no predicate supplied.
        Returns None if no element found (mirrors LINQ FirstOrDefault).
        """
        if predicate is None:
            return self[0] if len(self) > 0 else None
        for x in self:
            if predicate(x):
                return x
        return None

    # PascalCase alias for C# compatibility
    OrderByDifferentPackingGroupQuantityDescAndOccupation = ordered_by_different_packing_group_quantity_desc_and_occupation
    ordered_by_layer_remount_desc_and_occupation = OrderByLayerRemountDescAndOccupation
    ordered_by_not_remount_desc_and_occupation = OrderByNotRemountDescAndOccupation
    ordered_by_layer_and_difference = OrderByLayerAndDifference 
    ordered_by_layer_and_occupation = OrderByLayerAndOccupation
    ordered_by_layer_occupation_and_difference = OrderByLayerOccupationAndDifference
    first_or_default = FirstOrDefault
    with_same_type = WithSameType
    where_is_not = WhereIsNot
    OrderByDifferentPackingCodeQuantityDescAndProductQuantityDescAndOccupationDesc = order_by_different_packing_code_quantity_desc_and_product_quantity_desc_and_occupation_desc