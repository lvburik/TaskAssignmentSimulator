"""Convert an adjacent coordinate pair into a world movement action."""

def ToDirection(current_location: tuple[int, int], next_location: tuple[int, int]) -> str:
    """
    Converts a pair of locations into a direction string.

    Args:
        current_location (tuple[int, int]): The current location (x, y).
        next_location (tuple[int, int]): The next location (x, y).

    Returns:
        str: The direction to move from current_location to next_location.
             Possible values are "up", "down", "left", "right".
    """
    x1, y1 = current_location
    x2, y2 = next_location

    if x2 == x1 and y2 == y1 - 1:
        return "up"
    elif x2 == x1 and y2 == y1 + 1:
        return "down"
    elif x2 == x1 - 1 and y2 == y1:
        return "left"
    elif x2 == x1 + 1 and y2 == y1:
        return "right"
    else:
        raise ValueError("Invalid movement from {} to {}".format(current_location, next_location))