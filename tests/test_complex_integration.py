import pytest

from pydantic import ValidationError
from src.models import Apartment
from src.manager import Manager
from src.models import Parameters
from src.models import Bill


def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))


    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0


def test_get_apartment_costs_integration():

    params = Parameters()
    manager = Manager(params)
    assert manager.get_apartment_costs('apart-polanka', 1900, 1) == 0.0
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 760.0 + 150.0
    # test ponizej nie bedzie pass
    assert manager.get_apartment_costs('apart-polanka', 2027, 1) == 0.0
    assert manager.get_apartment_costs('apart-polanka', 2027, 15) == 0.0


def test_create_apartment_settlement_for_month_with_and_without_bills():
    manager = Manager(Parameters())

    settlement_with_bills = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    assert settlement_with_bills is not None
    assert settlement_with_bills.apartment == 'apart-polanka'
    assert settlement_with_bills.year == 2025
    assert settlement_with_bills.month == 1
    assert settlement_with_bills.total_rent_pln == 0.0
    assert settlement_with_bills.total_bills_pln == 910.0
    assert settlement_with_bills.total_due_pln == -910.0

    settlement_without_bills = manager.create_apartment_settlement('apart-polanka', 2025, 2)
    assert settlement_without_bills is not None
    assert settlement_without_bills.apartment == 'apart-polanka'
    assert settlement_without_bills.year == 2025
    assert settlement_without_bills.month == 2
    assert settlement_without_bills.total_rent_pln == 0.0
    assert settlement_without_bills.total_bills_pln == 0.0
    assert settlement_without_bills.total_due_pln == 0.0


def test_create_tenant_settlements_from_apartment_settlement():
    manager = Manager(Parameters())
    apartment_settlement = manager.create_apartment_settlement('apart-polanka', 2025, 1)

    settlements_many = manager.create_tenant_settlements(apartment_settlement)
    assert isinstance(settlements_many, list)
    assert len(settlements_many) == 3

    expected_share_many = 910.0 / 3.0
    tenant_ids = [settlement.tenant for settlement in settlements_many]
    assert 'tenant-1' in tenant_ids
    assert 'tenant-2' in tenant_ids
    assert 'tenant-3' in tenant_ids

    for settlement in settlements_many:
        assert settlement.apartment_settlement == 'apart-polanka'
        assert settlement.year == 2025
        assert settlement.month == 1
        assert settlement.rent_pln == 0.0
        assert settlement.bills_pln == pytest.approx(expected_share_many)
        assert settlement.total_due_pln == pytest.approx(expected_share_many)
        assert settlement.balance_pln == pytest.approx(-expected_share_many)

    manager.tenants = {'tenant-1': manager.tenants['tenant-1']}
    settlements_one = manager.create_tenant_settlements(apartment_settlement)
    assert isinstance(settlements_one, list)
    assert len(settlements_one) == 1
    assert settlements_one[0].tenant == 'tenant-1'
    assert settlements_one[0].bills_pln == 910.0
    assert settlements_one[0].total_due_pln == 910.0
    assert settlements_one[0].balance_pln == -910.0

    manager.tenants = {}
    settlements_none = manager.create_tenant_settlements(apartment_settlement)
    assert isinstance(settlements_none, list)
    assert len(settlements_none) == 0