# ...existing code...
from typing import Iterable

class OrderList(list):
    """Wrapper list with C#-like OrderedBy... methods used by rules."""
    def OrderedByNumber(self):
        return OrderList(sorted(self, key=lambda o: getattr(o, "Number", getattr(o, "MapNumber", 0))))

    def OrderedByNumberDescending(self):
        return OrderList(sorted(self, key=lambda o: getattr(o, "Number", getattr(o, "MapNumber", 0)), reverse=True))

    def OrderedByLicensePlate(self):
        # fallback keys: LicensePlate, license_plate, VehiclePlate
        return OrderList(sorted(self, key=lambda o: getattr(o, "LicensePlate",
                                                            getattr(o, "license_plate",
                                                                    getattr(o, "VehiclePlate", "")))))
    # snake_case aliases
    ordered_by_number = OrderedByNumber
    ordered_by_number_descending = OrderedByNumberDescending
    ordered_by_license_plate = OrderedByLicensePlate
