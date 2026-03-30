from src.models import Apartment, ApartmentSettlement, Bill, Parameters, Tenant, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key, year=None, month=None):
        if apartment_key not in self.apartments:
            return None

        total_cost = sum(
            bill.amount_pln for bill in self.bills 
            if bill.apartment == apartment_key and 
               (bill.settlement_year == year or year == None) and 
               (bill.settlement_month == month or month == None)
        )
        
        return float(total_cost)

    def create_apartment_settlement(self, apartment_key: str, year: int, month: int):
        if apartment_key not in self.apartments:
            return None

        total_bills_pln = self.get_apartment_costs(apartment_key, year, month)
        total_transfers_pln = 0.0
        balance_pln = total_transfers_pln - total_bills_pln

        return ApartmentSettlement(
            apartment=apartment_key,
            month=month,
            year=year,
            total_rent_pln=total_transfers_pln,
            total_bills_pln=total_bills_pln,
            total_due_pln=balance_pln,
        )
        
