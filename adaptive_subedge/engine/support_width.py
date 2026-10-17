"""Internal exact width aggregation for already-proven supported leaf rectangles."""
from fractions import Fraction
from typing import Callable


class _CoveredIntervals:
    """Coordinate-compressed coverage counts with longest connected union lengths."""

    def __init__(self, coordinates: tuple[Fraction, ...]):
        self.coordinates = coordinates
        self.interval_count = len(coordinates) - 1
        size = 4 * self.interval_count
        self.cover_count = [0] * size
        self.prefix = [Fraction(0)] * size
        self.suffix = [Fraction(0)] * size
        self.longest = [Fraction(0)] * size

    def update(self, first: int, last: int, delta: int) -> None:
        self._update(1, 0, self.interval_count - 1, first, last, delta)

    def _update(self, node: int, left: int, right: int,
                first: int, last: int, delta: int) -> None:
        if first <= left and right <= last:
            self.cover_count[node] += delta
        else:
            middle = (left + right) // 2
            if first <= middle:
                self._update(node * 2, left, middle, first, last, delta)
            if last > middle:
                self._update(node * 2 + 1, middle + 1, right, first, last, delta)
        self._pull(node, left, right)

    def _pull(self, node: int, left: int, right: int) -> None:
        if self.cover_count[node] > 0:
            length = self.coordinates[right + 1] - self.coordinates[left]
            self.prefix[node] = self.suffix[node] = self.longest[node] = length
        elif left == right:
            self.prefix[node] = self.suffix[node] = self.longest[node] = Fraction(0)
        else:
            middle = (left + right) // 2
            lower, upper = node * 2, node * 2 + 1
            lower_length = self.coordinates[middle + 1] - self.coordinates[left]
            upper_length = self.coordinates[right + 1] - self.coordinates[middle + 1]
            self.prefix[node] = self.prefix[lower]
            if self.prefix[lower] == lower_length:
                self.prefix[node] += self.prefix[upper]
            self.suffix[node] = self.suffix[upper]
            if self.suffix[upper] == upper_length:
                self.suffix[node] += self.suffix[lower]
            self.longest[node] = max(self.longest[lower], self.longest[upper],
                                     self.suffix[lower] + self.prefix[upper])


def _minimum_supported_width(
    rectangles: tuple[tuple[Fraction, Fraction, Fraction, Fraction], ...],
    check_cancelled: Callable[[], None],
) -> Fraction:
    """Minimum longest lateral union over [0,1]; inputs are validated internal leaves.

    Closed proven rectangles make the open-slab minimum conservative at event
    lines too. Cancellation exceptions propagate to the controller's owner.
    """
    events = {Fraction(0): [], Fraction(1): []}
    coordinates = set()
    for start, end, lower, upper in rectangles:
        events.setdefault(start, []).append((lower, upper, 1))
        events.setdefault(end, []).append((lower, upper, -1))
        coordinates.update((lower, upper))
    ordered_coordinates = tuple(sorted(coordinates))
    coordinate_indices = {value: index for index, value in enumerate(ordered_coordinates)}
    tree = _CoveredIntervals(ordered_coordinates) if rectangles else None
    ordered_events = sorted(events)
    minimum = None
    for index, event in enumerate(ordered_events):
        check_cancelled()
        # Apply every coincident change before observing the following slab.
        for lower, upper, delta in events[event]:
            tree.update(coordinate_indices[lower], coordinate_indices[upper] - 1, delta)
        if index + 1 < len(ordered_events):
            width = tree.longest[1] if tree is not None else Fraction(0)
            minimum = width if minimum is None else min(minimum, width)
    return minimum
