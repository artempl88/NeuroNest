"""
Константы приложения NeuroNest
"""

# NOTPUNKS Token константы
NOTPUNKS_DECIMALS = 9
NOTPUNKS_MULTIPLIER = 10 ** NOTPUNKS_DECIMALS

def to_minimal_units(amount: float) -> int:
    """Конвертация в минимальные единицы"""
    return int(amount * NOTPUNKS_MULTIPLIER)

def from_minimal_units(amount: int) -> float:
    """Конвертация из минимальных единиц"""
    return amount / NOTPUNKS_MULTIPLIER 