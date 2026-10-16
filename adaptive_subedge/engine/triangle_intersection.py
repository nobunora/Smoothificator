"""Exact closed triangle intersections and point/ray predicates in 3D."""
from .mesh_topology import _cross, _difference


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _normal(triangle):
    return _cross(_difference(triangle[1], triangle[0]), _difference(triangle[2], triangle[0]))


def _dominant_axis(vector):
    return max(range(3), key=lambda axis: abs(vector[axis]))


def _affine(a, b, t):
    return tuple(x+t*(y-x) for x, y in zip(a, b))


def _side(a, b, p, drop):
    i, j = (axis for axis in range(3) if axis != drop)
    return (b[i]-a[i])*(p[j]-a[j]) - (b[j]-a[j])*(p[i]-a[i])


def _triangle_sides(point, triangle):
    drop = _dominant_axis(_normal(triangle))
    sign = 1 if _side(*triangle, drop) > 0 else -1
    return tuple(sign*_side(triangle[i], triangle[(i+1) % 3], point, drop) for i in range(3))


def _point_on_triangle(point, triangle):
    return (_dot(_normal(triangle), _difference(point, triangle[0])) == 0
            and all(side >= 0 for side in _triangle_sides(point, triangle)))


def _point_on_segment(point, a, b):
    return (not any(_cross(_difference(point, a), _difference(b, a)))
            and all(min(x, y) <= p <= max(x, y) for p, x, y in zip(point, a, b)))


def _plane_slice(triangle, origin, normal):
    distances = tuple(_dot(normal, _difference(p, origin)) for p in triangle)
    points = {p for p, distance in zip(triangle, distances) if distance == 0}
    for i in range(3):
        j = (i+1) % 3
        if distances[i]*distances[j] < 0:
            points.add(_affine(triangle[i], triangle[j], distances[i]/(distances[i]-distances[j])))
    return tuple(sorted(points))


def _coplanar_intersection(subject, clip, normal):
    drop = _dominant_axis(normal)
    if _side(*clip, drop) < 0:
        clip = (clip[0], clip[2], clip[1])
    polygon = list(subject)
    for i in range(3):
        if not polygon:
            break
        a, b = clip[i], clip[(i+1) % 3]
        previous = polygon[-1]
        before = _side(a, b, previous, drop)
        clipped = []
        for current in polygon:
            after = _side(a, b, current, drop)
            if (before >= 0) != (after >= 0):
                clipped.append(_affine(previous, current, before/(before-after)))
            if after >= 0:
                clipped.append(current)
            previous, before = current, after
        # Carrying 3D affine points is exactly the shared-plane lift.
        polygon = list(dict.fromkeys(clipped))
    return tuple(polygon)


def _intersection_vertices(first, second):
    """Vertices spanning the complete convex intersection, including contacts."""
    first_normal, second_normal = _normal(first), _normal(second)
    direction = _cross(first_normal, second_normal)
    if not any(direction):
        if _dot(first_normal, _difference(second[0], first[0])) != 0:
            return ()
        return _coplanar_intersection(first, second, first_normal)
    first_slice = _plane_slice(first, second[0], second_normal)
    second_slice = _plane_slice(second, first[0], first_normal)
    if not first_slice or not second_slice:
        return ()
    axis = _dominant_axis(direction)
    first_slice = sorted(first_slice, key=lambda p: p[axis])
    second_slice = sorted(second_slice, key=lambda p: p[axis])
    lower = max(first_slice[0][axis], second_slice[0][axis])
    upper = min(first_slice[-1][axis], second_slice[-1][axis])
    if lower > upper:
        return ()
    source = first_slice if len(first_slice) > 1 else second_slice
    if len(source) == 1:
        return (source[0],) if first_slice[0] == second_slice[0] else ()
    a, b = source[0], source[-1]
    return tuple(dict.fromkeys(_affine(a, b, (coordinate-a[axis])/(b[axis]-a[axis]))
                               for coordinate in (lower, upper)))


def _ray_hit(point, direction, triangle):
    normal = _normal(triangle)
    numerator = _dot(normal, _difference(triangle[0], point))
    denominator = _dot(normal, direction)
    if denominator == 0:
        return "ambiguous" if numerator == 0 else "miss"
    t = numerator / denominator
    if t <= 0:
        return "miss"
    hit = tuple(p+t*d for p, d in zip(point, direction))
    sides = _triangle_sides(hit, triangle)
    if any(side < 0 for side in sides):
        return "miss"
    return "ambiguous" if any(side == 0 for side in sides) else "hit"
