import pytest
from trading_agent.risk import position_size_units, historical_loss_rate

def test_position_size():
    assert position_size_units(1000, 1, 1.10, 1.09) == pytest.approx(1000)

def test_loss_rate():
    assert historical_loss_rate(["WIN", "LOSS", "LOSS"]) == pytest.approx(2/3)

def test_no_resolved_trades():
    assert historical_loss_rate(["OPEN", "BREAKEVEN"]) is None

def test_invalid_stop():
    with pytest.raises(ValueError):
        position_size_units(1000, 1, 1.10, 1.10)
