"""Small reversible world-space trials, not recovered source geometry."""
from dataclasses import dataclass, asdict
import math

@dataclass(frozen=True)
class Parameters:
    belly_dz: float = 0.0
    shoulder_fraction: float = 0.0
    half_length: float = 4.65
    belly_center: float = 0.0
    belly_radius: float = 0.65
    shoulder_center: float = -0.68
    shoulder_radius: float = 0.27

    def validate(self):
        assert all(math.isfinite(v) for v in asdict(self).values())
        assert abs(self.belly_dz) <= 0.12
        assert -0.12 <= self.shoulder_fraction <= 0.15
        assert self.half_length > 0 and self.belly_radius > 0 and self.shoulder_radius > 0
        # Trial support must not move either endpoint.
        assert abs(self.belly_center) + self.belly_radius < 1
        assert abs(self.shoulder_center) + self.shoulder_radius < 1

def bump(u, center, radius):
    t = (u - center) / radius
    return (1 - t*t)**3 if abs(t) < 1 else 0.0

def factors(x, p):
    u = x / p.half_length
    width = 1 + p.shoulder_fraction * bump(u, p.shoulder_center, p.shoulder_radius)
    dz = p.belly_dz * bump(u, p.belly_center, p.belly_radius)
    return width, dz

def forward(point, p):
    x, y, z = point
    width, dz = factors(x, p)
    return (x, y * width, z + dz)

def inverse(point, p):
    x, y, z = point
    width, dz = factors(x, p)
    return (x, y / width, z - dz)

def jacobian_determinant(x, p):
    # For this smooth map x'=x, y'=a(x)y, z'=z+b(x), det J=a(x)>0.
    # This statement concerns the continuous map, not the piecewise-linear
    # mesh approximation or any source, thickness or water-contact truth.
    return factors(x, p)[0]
