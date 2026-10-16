def position_size_units(account_balance: float, risk_pct: float, entry_price: float, stop_price: float) -> float:
    """Approximate units for quote-currency P/L; broker contract specs may change this."""
    if account_balance <= 0:
        raise ValueError("account_balance must be positive")
    if not 0 < risk_pct <= 100:
        raise ValueError("risk_pct must be greater than 0 and at most 100")
    distance = abs(entry_price - stop_price)
    if distance <= 0:
        raise ValueError("entry_price and stop_price must differ")
    return (account_balance * risk_pct / 100) / distance

def historical_loss_rate(outcomes: list[str]) -> float | None:
    """Observed loss fraction among resolved outcomes, not a forecast."""
    resolved = [item.upper() for item in outcomes if item.upper() in {"WIN", "LOSS"}]
    if not resolved:
        return None
    return resolved.count("LOSS") / len(resolved)
