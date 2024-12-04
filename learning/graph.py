import dataclasses
import numpy as np
from typing import List

@dataclasses.dataclass
class Point:
    t: float
    x: float
    y: float
    is_point: bool = False
    color: str = ''
    
    
def generate_points(A: float, a: float, B: float, b: float, 
                   phase: float, n_sampled: int,
                   noise: float) -> List[Point]:
    """
    Generate points based on parametric equations with selective sampling.
    """
    n_points = 2000

    # Convert phase to radians
    phase_rad = np.deg2rad(phase)
    
    # Generate time points
    t = np.linspace(0, 2*np.pi, n_points)
    
    # Generate coordinates
    x = A * np.cos(a * t)
    y = B * np.sin(b * t + phase_rad)
    
    # Create list of all points (initially not marked)
    gt_points = [Point(float(t[i]), float(x[i]), float(y[i]), False, '') 
             for i in range(n_points)]
    
    # Randomly select n_sampled points to be marked
    smp_points = []
    for idx in np.linspace(0, len(gt_points)-1, n_sampled, dtype=int):
        # Copy an existing point, add noise, mark it as a point.
        point = dataclasses.replace(gt_points[idx])
        point.x += np.random.normal(0, np.sqrt(noise))
        point.y += np.random.normal(0, np.sqrt(noise))
        point.is_point = True
        point.color = '0xFFCC66'
        smp_points.append(point)
    
    return gt_points, smp_points