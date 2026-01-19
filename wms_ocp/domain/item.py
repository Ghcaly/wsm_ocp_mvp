from __future__ import annotations
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional
from .product import Product


class Item:
    def __init__(
        self,
        Code: int,
        Amount: int = 0,
        OcpDefaultPerUni42: Decimal = Decimal(0),
        AmountRemaining: int = 0,
        LayersRemaining: int = 0,
        Splitted: bool = False,
        LicensePlate: str = "",
        MapNumber: str = "",
        Customer: str = "",
        ClientQuantity: Optional[Dict[int, int]] = None,
        DeliveryOrderSafeSide: Optional[Dict[int, int]] = None,
        DeliveryOrdersClient: Optional[Dict[int, str]] = None,
        Product: Product = Product(),
        DetachedAmount: int = 0,
        UnitAmount: int = 0,
        AmountPerContainer: int = 0,
        Factor: Decimal = Decimal(0),
        AdditionalOccupation: Decimal = Decimal(0),
        Realocated: bool = False,
        # snake_case overrides
        code: Optional[int] = None,
        amount: Optional[int] = None,
        ocp_default_per_uni42: Optional[Decimal] = None,
        amount_remaining: Optional[int] = None,
        layers_remaining: Optional[int] = None,
        splitted: Optional[bool] = None,
        license_plate: Optional[str] = None,
        map_number: Optional[str] = None,
        customer: Optional[str] = None,
        client_quantity: Optional[Dict[int, int]] = None,
        delivery_order_safe_side: Optional[Dict[int, int]] = None,
        delivery_orders_client: Optional[Dict[int, str]] = None,
        product: Optional[Product] = None,
        detached_amount: Optional[int] = None,
        unit_amount: Optional[int] = None,
        amount_per_container: Optional[int] = None,
        factor: Optional[Decimal] = None,
        additional_occupation: Optional[Decimal] = None,
        realocated: Optional[bool] = None,
    ):
        # prefer snake_case args when provided
        self._code = int(code) if code is not None else int(Code)
        self._amount = int(amount) if amount is not None else int(Amount)
        self._ocp_default_per_uni42 = Decimal(ocp_default_per_uni42) if ocp_default_per_uni42 is not None else Decimal(OcpDefaultPerUni42)
        self._amount_remaining = int(amount_remaining) if amount_remaining is not None else int(AmountRemaining)
        self._layers_remaining = int(layers_remaining) if layers_remaining is not None else int(LayersRemaining)
        self._splitted = bool(splitted) if splitted is not None else bool(Splitted)
        self._license_plate = license_plate if license_plate is not None else LicensePlate
        self._map_number = map_number if map_number is not None else MapNumber
        self._customer = customer if customer is not None else Customer
        self._client_quantity = dict(client_quantity or ClientQuantity or {})
        self._delivery_orders = {}
        self._delivery_orders_detached = {}
        self._delivery_order_safe_side = dict(delivery_order_safe_side or DeliveryOrderSafeSide or {})
        self._delivery_orders_client = dict(delivery_orders_client or DeliveryOrdersClient or {})
        self._product = product if product is not None else Product
        self._detached_amount = int(detached_amount) if detached_amount is not None else int(DetachedAmount)
        self._unit_amount = int(unit_amount) if unit_amount is not None else int(UnitAmount)
        self._amount_per_container = int(amount_per_container) if amount_per_container is not None else int(AmountPerContainer)
        self._factor = Decimal(factor) if factor is not None else Decimal(Factor)
        self._additional_occupation = Decimal(additional_occupation) if additional_occupation is not None else Decimal(AdditionalOccupation)
        self._realocated = bool(realocated) if realocated is not None else bool(Realocated)

    # PascalCase properties mapping to private fields
    @property
    def Code(self) -> int:
        return self._code

    @Code.setter
    def Code(self, v: int):
        self._code = int(v)

    @property
    def Amount(self) -> int:
        return int(self._amount)

    @Amount.setter
    def Amount(self, v: int):
        self._amount = int(v)

    @property
    def OcpDefaultPerUni42(self) -> Decimal:
        return Decimal(self._ocp_default_per_uni42)

    @OcpDefaultPerUni42.setter
    def OcpDefaultPerUni42(self, v: Decimal):
        self._ocp_default_per_uni42 = Decimal(v)

    @property
    def AmountRemaining(self) -> int:
        return int(self._amount_remaining)

    @AmountRemaining.setter
    def AmountRemaining(self, v: int):
        self._amount_remaining = int(v)

    @property
    def LayersRemaining(self) -> int:
        return int(self._layers_remaining)

    @LayersRemaining.setter
    def LayersRemaining(self, v: int):
        self._layers_remaining = int(v)

    @property
    def DetachedAmount(self) -> int:
        return int(self._detached_amount)

    @DetachedAmount.setter
    def DetachedAmount(self, v: int):
        self._detached_amount = int(v)

    @property
    def Product(self) -> Product:
        return self._product

    @Product.setter
    def Product(self, p: Product):
        self._product = p

    @property
    def ClientQuantity(self) -> Dict[int,int]:
        return dict(self._client_quantity)

    @ClientQuantity.setter
    def ClientQuantity(self, v: Dict[int,int]):
        self._client_quantity = dict(v or {})

    @property
    def DeliveryOrderSafeSide(self) -> Dict[int,int]:
        return dict(self._delivery_order_safe_side)

    @DeliveryOrderSafeSide.setter
    def DeliveryOrderSafeSide(self, v: Dict[int,int]):
        self._delivery_order_safe_side = dict(v or {})

    @property
    def DeliveryOrdersClient(self) -> Dict[int,str]:
        return dict(self._delivery_orders_client)

    @DeliveryOrdersClient.setter
    def DeliveryOrdersClient(self, v: Dict[int,str]):
        self._delivery_orders_client = dict(v or {})

    # keep previous snake_case aliases (they reference PascalCase props which now map to private fields)

    def DeliveryOrdersWithAmount(self) -> Iterable[int]:
        return [k for k, v in self._delivery_orders.items() if v > 0]

    def DeliveryOrdersWithDetachedAmount(self) -> Iterable[int]:
        return [k for k, v in self._delivery_orders_detached.items() if v > 0]

    def SubtractDeliveryOrderAmount(self, deliveryOrder: int, amount: int) -> int:
        return self._subtract_delivery_order_amount_from_dict(self._delivery_orders, deliveryOrder, amount, "map")

    def SubtractDeliveryOrderAmountDetached(self, deliveryOrder: int, amount: int) -> int:
        return self._subtract_delivery_order_amount_from_dict(self._delivery_orders_detached, deliveryOrder, amount, "map")

    def _subtract_delivery_order_amount_from_dict(self, delivery_dict: Dict[int, int], deliveryOrder: int, amount: int, map_context: str) -> int:
        if deliveryOrder not in delivery_dict:
            raise ValueError(f"DeliveryOrder {deliveryOrder} not found in {map_context}")
        prev = delivery_dict[deliveryOrder]
        new_value = max(0, prev - amount)
        delivery_dict[deliveryOrder] = new_value
        return new_value

    def Clone(self) -> "Item":
        cloned = Item(
            Code=self.Code,
            Amount=self.Amount,
            OcpDefaultPerUni42=self.OcpDefaultPerUni42,
            AmountRemaining=self.AmountRemaining,
            LayersRemaining=self.LayersRemaining,
            Splitted=self.Splitted,
            LicensePlate=self.LicensePlate,
            MapNumber=self.MapNumber,
            Customer=self.Customer,
            ClientQuantity=dict(self.ClientQuantity),
            DeliveryOrderSafeSide=dict(self.DeliveryOrderSafeSide),
            DeliveryOrdersClient=dict(self.DeliveryOrdersClient),
            Product=self.Product,
            DetachedAmount=self.DetachedAmount,
            UnitAmount=self.UnitAmount,
            AmountPerContainer=self.AmountPerContainer,
            Factor=self.Factor,
            AdditionalOccupation=self.AdditionalOccupation,
            Realocated=self.Realocated,
        )
        cloned._delivery_orders = dict(self._delivery_orders)
        cloned._delivery_orders_detached = dict(self._delivery_orders_detached)
        return cloned

    def HasAmountRemaining(self) -> bool:
        return self.AmountRemaining > 0

    def HasDetachedAmount(self) -> bool:
        return self.DetachedAmount > 0

    def Split(self):
        self.Splitted = True

    def SetCustomer(self, customer: str):
        self.Customer = customer

    def SetOcpDefaultPerUni42(self, occupation: Decimal):
        self.OcpDefaultPerUni42 = occupation

    def GetDeliveryOrders(self, side: Any) -> List[int]:
        # Conservative default: return all delivery orders where safe side equals provided side
        return [d for d, s in self.DeliveryOrderSafeSide.items() if s == side]

    def DeliveryOrdersWithDetached(self) -> Iterable[int]:
        return (d for d, q in self.ClientQuantity.items() if q == 0 and self.DetachedAmount > 0)

    def SetRealocated(self, realocated: bool):
        self.Realocated = realocated

    def SetAdditionalOccupation(self, ocupacaoAMais: Decimal):
        self.AdditionalOccupation = ocupacaoAMais

    # Additional methods that mutate stock/amounts
    def AddDeliveryOrder(self, deliveryOrder: int, amount: int, detachedAmount: int):
        if deliveryOrder in self._delivery_orders:
            self._delivery_orders[deliveryOrder] += amount
        else:
            self._delivery_orders[deliveryOrder] = amount

        if deliveryOrder in self._delivery_orders_detached:
            self._delivery_orders_detached[deliveryOrder] += detachedAmount
        else:
            self._delivery_orders_detached[deliveryOrder] = detachedAmount
        
        self.ClientQuantity[deliveryOrder] = self.ClientQuantity.get(deliveryOrder, 0) + amount
        # self.DetachedAmount += detachedAmount

    def AddAmount(self, amount: int, detachedAmount: int, unitAmount: int):
        self.Amount += amount
        self.AmountRemaining += amount
        self.DetachedAmount += detachedAmount
        self.UnitAmount = unitAmount

    def SubtractAmount(self, amountToSubtract: int):
        self.Amount = max(0, self.Amount - amountToSubtract)
        self.AmountRemaining = max(0, self.AmountRemaining - amountToSubtract)

    def GetClientDeliveryOrder(self, client: int) -> int:
        # Return the first delivery order for this client if present
        for d, c in self.DeliveryOrdersClient.items():
            if c == client:
                return d
        return -1

    def GetDeliveryOrderClient(self, deliveryOrder: int) -> str:
        return self.DeliveryOrdersClient.get(deliveryOrder, "")

    def IsDeliveryOrderClient(self, deliveryOrder: int, client: str) -> bool:
        return self.DeliveryOrdersClient.get(deliveryOrder) == client

    def AddDeliveryOrderClient(self, deliveryOrder: int, client: str):
        self.DeliveryOrdersClient[deliveryOrder] = client

    def AddDeliveryOrderSafeSide(self, deliveryOrder: int, safeSide: int):
        self.DeliveryOrderSafeSide[deliveryOrder] = safeSide

    def AddClientQuantity(self, clientCode: str, quantity: int):
        try:
            key = int(clientCode)
        except Exception:
            # if cannot convert, store as -1 keyed count under a numeric key
            key = -1
        # self.ClientQuantity[key] = self.ClientQuantity.get(key, 0) + quantity
        self._client_quantity[key] = self._client_quantity.get(key, 0) + quantity

    def SubtractClientQuantity(self, clientCode: int, quantity: int):
        prev = self.ClientQuantity.get(clientCode, 0)
        self.ClientQuantity[clientCode] = max(0, prev - quantity)

    def GetDeliveryOrdersWithAmount(self):
        return [d for d, q in self.ClientQuantity.items() if q > 0]

    # --- pythonic aliases for attributes -----------------------------
    @property
    def code(self) -> int:
        return self.Code

    @code.setter
    def code(self, v: int):
        self.Code = v

    @property
    def amount(self) -> int:
        return self.Amount

    @amount.setter
    def amount(self, v: int):
        self.Amount = v

    @property
    def amount_remaining(self) -> int:
        return self.AmountRemaining

    @amount_remaining.setter
    def amount_remaining(self, v: int):
        self.AmountRemaining = v

    @property
    def detached_amount(self) -> int:
        return self.DetachedAmount

    @detached_amount.setter
    def detached_amount(self, v: int):
        self.DetachedAmount = v

    @property
    def product(self) -> Product:
        return self.Product

    @product.setter
    def product(self, p: Product):
        self.Product = p

    # --- pythonic method aliases ------------------------------------
    def add_delivery_order(self, delivery_order: int, amount: int, detached_amount: int):
        return self.AddDeliveryOrder(delivery_order, amount, detached_amount)

    def add_amount(self, amount: int, detached_amount: int, unit_amount: int):
        return self.AddAmount(amount, detached_amount, unit_amount)

    def subtract_amount(self, amount_to_subtract: int):
        return self.SubtractAmount(amount_to_subtract)

    def get_client_delivery_order(self, client: int) -> int:
        return self.GetClientDeliveryOrder(client)

    def get_delivery_order_client(self, delivery_order: int) -> str:
        return self.GetDeliveryOrderClient(delivery_order)

    def is_delivery_order_client(self, delivery_order: int, client: str) -> bool:
        return self.IsDeliveryOrderClient(delivery_order, client)

    def add_delivery_order_client(self, delivery_order: int, client: str):
        return self.AddDeliveryOrderClient(delivery_order, client)

    def add_delivery_order_safe_side(self, delivery_order: int, safe_side: int):
        return self.AddDeliveryOrderSafeSide(delivery_order, safe_side)

    def add_client_quantity(self, client_code: str, quantity: int):
        return self.AddClientQuantity(client_code, quantity)

    def subtract_client_quantity(self, client_code: int, quantity: int):
        return self.SubtractClientQuantity(client_code, quantity)

    def delivery_orders_with_amount(self):
        return self.GetDeliveryOrdersWithAmount()

    # --- additional snake_case aliases for remaining PascalCase methods ---
    def clone(self) -> "Item":
        return self.Clone()

    def has_amount_remaining(self) -> bool:
        return self.HasAmountRemaining()

    def has_detached_amount(self) -> bool:
        return self.HasDetachedAmount()

    def split(self):
        return self.Split()

    def set_customer(self, customer: str):
        return self.SetCustomer(customer)

    def set_ocp_default_per_uni42(self, occupation: Decimal):
        return self.SetOcpDefaultPerUni42(occupation)

    def get_delivery_orders(self, side: Any) -> List[int]:
        return self.GetDeliveryOrders(side)

    def delivery_orders_with_detached(self):
        return self.DeliveryOrdersWithDetached()

    def set_realocated(self, realocated: bool):
        return self.SetRealocated(realocated)

    def set_additional_occupation(self, ocupacaoAMais: Decimal):
        return self.SetAdditionalOccupation(ocupacaoAMais)

    # --- Extension methods from C# ItemExtensions ---
    
    # Type checking methods (delegate to Product)
    def IsChopp(self) -> bool:
        """Check if item's product is Chopp"""
        return self.Product.IsChopp() if self.Product else False
    
    def is_chopp(self) -> bool:
        return self.IsChopp()
    
    def NotChopp(self) -> bool:
        """Check if item's product is NOT Chopp"""
        return not self.IsChopp()
    
    def not_chopp(self) -> bool:
        return self.NotChopp()

    def isDisposable(self) -> bool:
        """Check if item's product is Disposable"""
        return self.Product.is_disposable() if self.Product else False

    def is_disposable(self) -> bool:
        """Check if item's product is Disposable"""
        return self.isDisposable()

    def IsIsotonicWater(self) -> bool:
        """Check if item's product is IsotonicWater"""
        return self.Product.is_isotonic_water() if self.Product else False
    
    def is_isotonic_water(self) -> bool:
        return self.IsIsotonicWater()
    
    def NotIsotonicWater(self) -> bool:
        """Check if item's product is NOT IsotonicWater"""
        return not self.IsIsotonicWater()
    
    def not_isotonic_water(self) -> bool:
        return self.NotIsotonicWater()
    
    def isReturnable(self) -> bool:
        """Check if item's product is Returnable"""
        return self.Product.is_returnable() if self.Product else False
    
    def IsReturnable(self) -> bool:
        return self.isReturnable()
    
    def isTopOfPallet(self) -> bool:
        """Check if item's product is Returnable"""
        return self.Product.IsTopOfPallet() if self.Product else False
    
    def IsTopOfPallet(self) -> bool:
        return self.isTopOfPallet()
    
    def is_returnable(self) -> bool:
        return self.isReturnable()
    
    def IsPackage(self) -> bool:
        """Check if item's product is Package"""
        return self.Product.is_package() if self.Product else False
    
    def is_package(self) -> bool:
        return self.IsPackage()
    
    def IsBoxTemplate(self) -> bool:
        """Check if item's product is BoxTemplate"""
        return self.Product.is_box_template() if self.Product else False
    
    def is_box_template(self) -> bool:
        return self.IsBoxTemplate()
    
    def NotMarketplace(self) -> bool:
        """Check if item's product is NOT marketplace (not Package and not BoxTemplate)"""
        return self.Product.not_marketplace() if self.Product else True
    
    def not_marketplace(self) -> bool:
        return self.NotMarketplace()
    
    # Configuration and layer methods
    def WithConfiguration(self, includeTopOfPallet: bool) -> bool:
        """
        C#: includeTopOfPallet || !item.Product.PalletSetting.IncludeTopOfPallet
        """
        if not self.Product or not self.Product.PalletSetting:
            return includeTopOfPallet
        return includeTopOfPallet or not self.Product.PalletSetting.IncludeTopOfPallet
    
    def with_configuration(self, include_top_of_pallet: bool) -> bool:
        return self.WithConfiguration(include_top_of_pallet)
    
    def WithLayerCode(self) -> bool:
        """Check if product has LayerCode > 0"""
        return self.Product.LayerCode > 0 if self.Product else False
    
    def with_layer_code(self) -> bool:
        return self.WithLayerCode()
    
    def WithoutLayerCode(self) -> bool:
        """Check if product has LayerCode == 0"""
        return self.Product.LayerCode == 0 if self.Product else True
    
    def without_layer_code(self) -> bool:
        return self.WithoutLayerCode()
    
    # Amount checking methods
    def WithAmountRemaining(self) -> bool:
        """Check if item has amount remaining"""
        return self.HasAmountRemaining()
    
    def with_amount_remaining(self) -> bool:
        return self.WithAmountRemaining()
    
    def WithDetachedAmount(self) -> bool:
        """Check if item has detached amount > 0"""
        return self.DetachedAmount > 0
    
    def with_detached_amount(self) -> bool:
        return self.WithDetachedAmount()
    
    def WithAmountRemainingOrDetachedAmount(self) -> bool:
        """
        C#: x.HasAmountRemaining() || x.HasDetachedAmount() || 
            (x.Product is IBoxTemplate) && ((IBoxTemplate)x.Product).ItemsInBox.Any(...)
        """
        if self.HasAmountRemaining() or self.HasDetachedAmount():
            return True
        
        # Check BoxTemplate special case
        if self.Product and self.Product.is_box_template():
            items_in_box = getattr(self.Product, 'ItemsInBox', [])
            for box_item in items_in_box:
                delivery_orders = getattr(box_item, 'DeliveryOrders', [])
                if any(getattr(do, 'DetachedAmount', 0) > 0 for do in delivery_orders):
                    return True
        
        return False
    
    def with_amount_remaining_or_detached_amount(self) -> bool:
        return self.WithAmountRemainingOrDetachedAmount()
    
    def WithCalculateAdditionalOccupation(self) -> bool:
        """Check if product has CalculateAdditionalOccupation enabled"""
        return self.Product.CalculateAdditionalOccupation if self.Product else False
    
    def with_calculate_additional_occupation(self) -> bool:
        return self.WithCalculateAdditionalOccupation()
    
    def CanBePalletized(self) -> bool:
        """Check if product can be palletized"""
        return self.Product.CanBePalletized if self.Product else False
    
    def can_be_palletized(self) -> bool:
        return self.CanBePalletized()
    
    # Adicione após os aliases de properties existentes (após def product(self))

    @property
    def Customer(self) -> str:
        return self._customer

    @Customer.setter
    def Customer(self, v: str):
        self._customer = str(v)
        
    @property
    def splitted(self) -> bool:
        return self.Splitted

    @splitted.setter
    def splitted(self, v: bool):
        self.Splitted = v

    @property
    def license_plate(self) -> str:
        return self.LicensePlate

    @license_plate.setter
    def license_plate(self, v: str):
        self.LicensePlate = v

    @property
    def map_number(self) -> str:
        return self._map_number
    
    @property
    def MapNumber(self) -> str:
        return self.map_number
    
    @map_number.setter
    def map_number(self, v: str):
        self._map_number = v

    @property
    def customer(self) -> str:
        return self.Customer

    @customer.setter
    def customer(self, v: str):
        self.Customer = v

    @property
    def layers_remaining(self) -> int:
        return self.LayersRemaining

    @layers_remaining.setter
    def layers_remaining(self, v: int):
        self.LayersRemaining = v

    @property
    def unit_amount(self) -> int:
        return self.UnitAmount

    @unit_amount.setter
    def unit_amount(self, v: int):
        self.UnitAmount = v

    @property
    def amount_per_container(self) -> int:
        return self.AmountPerContainer

    @amount_per_container.setter
    def amount_per_container(self, v: int):
        self.AmountPerContainer = v

    @property
    def factor(self) -> Decimal:
        return self._factor

    @factor.setter
    def factor(self, v: Decimal):
        self._factor = v

    @factor.setter
    def Factor(self, v: Decimal):
        self._factor = v

    @property
    def Factor(self) -> Decimal:
        return self._factor
    
    @property
    def additional_occupation(self) -> Decimal:
        return self.AdditionalOccupation

    @additional_occupation.setter
    def additional_occupation(self, v: Decimal):
        self.AdditionalOccupation = v

    @property
    def realocated(self) -> bool:
        return self.Realocated

    @realocated.setter
    def realocated(self, v: bool):
        self.Realocated = v
