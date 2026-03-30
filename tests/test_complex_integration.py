import pytest

from pydantic import ValidationError
from src.models import Apartment
from src.manager import Manager
from src.models import Parameters

def test_get_apartment_costs_integration():
    params = Parameters()
    manager = Manager(params)
    assert manager.get_apartment_costs('apart-polanka', 1900, 1) == 0.0
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 760.0 + 150.0
    # test ponizej nie bedzie pass
    assert manager.get_apartment_costs('apart-polanka', 2027, 1) == 0.0