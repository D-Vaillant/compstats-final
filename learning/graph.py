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
                   phase: float, n_sampled: int) -> List[Point]:
    """
    Generate points based on parametric equations with selective sampling.
    """
    n_points = 2500

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
        point = dataclasses.replace(gt_points[idx])
        point.is_point = True
        point.color = '0xFFCC66'
        smp_points.append(point)
        
    # if n_sampled > 0:
    #     # Evenly space the sampled points
    #     sample_indices = np.linspace(0, len(points)-1, n_sampled, dtype=int)
    #     colors = ['#%06x' % np.random.randint(0, 0xFFFFFF) for _ in range(n_sampled)]
        
    #     for idx, color in zip(sample_indices, colors):
    #         points[idx].is_point = True
    #         points[idx].color = '0xFFCC66'
    
    return gt_points, smp_points