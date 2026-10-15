"""Write only a synthetic closed 10 x 10 x 2 mm coupon for offline slicing."""

from pathlib import Path


def main():
    vertices = ((0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0),
                (0, 0, 2), (10, 0, 2), (10, 10, 2), (0, 10, 2))
    triangles = ((0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
                 (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
                 (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7))
    lines = ["solid smoothificator_offline_coupon"]
    for triangle in triangles:
        a, b, c = [vertices[index] for index in triangle]
        u = tuple(b[i] - a[i] for i in range(3))
        v = tuple(c[i] - a[i] for i in range(3))
        cross = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        length = sum(component**2 for component in cross) ** 0.5
        normal = " ".join(str(component / length) for component in cross)
        lines.extend((f"facet normal {normal}", "outer loop"))
        lines.extend("vertex " + " ".join(map(str, point)) for point in (a, b, c))
        lines.extend(("endloop", "endfacet"))
    lines.append("endsolid smoothificator_offline_coupon")
    output = Path(__file__).resolve().parents[1] / "artifacts/fixtures/offline-coupon.stl"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="ascii", newline="\n") as stream:
        stream.write("\n".join(lines) + "\n")
    print("Created synthetic offline coupon (10 x 10 x 2 mm); no printer operation.")


if __name__ == "__main__":
    main()
