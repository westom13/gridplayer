"""Calculate stereo balance based on grid position."""

from enum import Enum


class GridColumn(Enum):
    LEFT = -1.0
    CENTER = 0.0
    RIGHT = 1.0


def calculate_balance_from_grid_position(
    block_index: int, total_blocks: int
) -> float:
    """
    Calculate stereo balance (-1.0 to 1.0) based on video position in grid.
    
    Uses a smooth distribution across the stereo field.
    
    Args:
        block_index: Position of the block in the grid (0-based)
        total_blocks: Total number of blocks in the grid
    
    Returns:
        Pan value from -1.0 (full left) to 1.0 (full right)
    
    Examples:
        >>> calculate_balance_from_grid_position(0, 1)
        0.0
        >>> calculate_balance_from_grid_position(0, 3)
        -1.0
        >>> calculate_balance_from_grid_position(1, 3)
        0.0
        >>> calculate_balance_from_grid_position(2, 3)
        1.0
        >>> calculate_balance_from_grid_position(0, 5)
        -1.0
        >>> calculate_balance_from_grid_position(2, 5)
        0.0
        >>> calculate_balance_from_grid_position(4, 5)
        1.0
    """
    if total_blocks <= 1:
        return GridColumn.CENTER.value
    
    # Normalize position to 0-1 range
    normalized_pos = block_index / (total_blocks - 1)
    
    # Convert to -1 to 1 range
    balance = (normalized_pos * 2.0) - 1.0
    
    # Optional: Apply smoothing curve for better distribution
    # balance = _smooth_curve(balance)
    
    return balance


def _smooth_curve(balance: float) -> float:
    """Apply smoothing curve to balance distribution."""
    # You can use various curves:
    # Linear: return balance
    # Sine curve (smooth): return sin(balance * π/2)
    # Quadratic: return balance ** 2 if balance > 0 else -((-balance) ** 2)
    
    import math
    return math.sin(balance * math.pi / 2)


def get_grid_column(balance: float) -> GridColumn:
    """Determine primary grid column from balance value."""
    if balance < -0.3:
        return GridColumn.LEFT
    elif balance > 0.3:
        return GridColumn.RIGHT
    else:
        return GridColumn.CENTER


def get_balance_percentage(balance: float) -> tuple[str, int]:
    """
    Get human-readable balance description.
    
    Returns:
        Tuple of (description, percentage) where percentage is 0-100
        0 = full left, 50 = center, 100 = full right
    """
    percentage = int((balance + 1.0) / 2.0 * 100)
    
    if balance < -0.3:
        desc = "Left"
    elif balance > 0.3:
        desc = "Right"
    else:
        desc = "Center"
    
    return desc, percentage