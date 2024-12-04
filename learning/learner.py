import numpy as np
from typing import List, Tuple, Dict
from learning.graph import Point


class KernelRegressor:
    def __init__(self, bandwidth: float = 0.1,
                 kernel_choice: str = 'normal'):
        """
        Initialize the nonparametric regressor.
        Args:
            bandwidth: Smoothing parameter for the regression
            kernel_choice: Chooses the kernel.
        """
        self.bandwidth = bandwidth
        self.K = self.kernels[kernel_choice]

    @property
    def kernels(self):
        return {
            'normal': lambda t: np.exp(-0.5 * t**2) / np.sqrt(2 * np.pi),
            'quartic': lambda t: np.where(np.abs(t) <= 1, (15/16) * ((1 - t**2)**2), 0),
            'parabolic': lambda t: np.where(np.abs(t) <= 1, 0.75 * (1 - t**2), 0),
            'cosine': lambda t: np.where(np.abs(t) <= 1, (np.pi/4)*np.cos((np.pi*t)/2), 0),
        }

    def fit_predict(self, sampled_points: List[Point], num_output_points: int = 1000) -> List[Point]:
        """
        Fit the nonparametric regression and generate smooth curve points.
        
        Args:
            sampled_points: List of Point objects containing the sampled data
            num_output_points: Number of points to generate for the smooth curve
        
        Returns:
            List of Points containing the smooth curve and original sampled points
        """
        # Extract coordinates from sampled points
        t_data = np.array([p.t for p in sampled_points])
        x_data = np.array([p.x for p in sampled_points])
        y_data = np.array([p.y for p in sampled_points])

        # Right now, we hardcode the range of 0 to 2*np.pi for the purposes of the t input
        # and the kernel function. That's fine, probably!
        
        K_h = lambda t: (1/self.bandwidth) * self.K(t / (self.bandwidth))
        
        t_smooth = np.linspace(0, 2*np.pi, num_output_points)
        
        x_smooth = np.zeros(len(t_smooth))
        y_smooth = np.zeros(len(t_smooth))
        for i, t in enumerate(t_data):
            weights = self.K((t - t_data) / self.bandwidth)
            x_smooth[i] = np.sum(x_data * weights) / np.sum(weights)
            y_smooth[i] = np.sum(y_data * weights) / np.sum(weights)


        fitted_points = []
        for t, x, y in zip(t_smooth, x_smooth, y_smooth):
            fitted_points.append(Point(t, x, y, color='#FF4433'))
        
        # # Add back the original sampled points with their colors
        # for point in sampled_points:
        #     if point.is_point:
        #         fitted_points.append(Point(
        #             x=point.x,
        #             y=point.y,
        #             is_point=True,
        #             color=point.color
        #         ))
        
        return fitted_points

def fit_curve(sampled_points: List[Point],
              bandwidth: float = 0.1,
              kernel: str = 'normal') -> List[Point]:
    """
    Wrapper function to maintain the same interface.
    """
    regressor = KernelRegressor(bandwidth=bandwidth, kernel_choice=kernel)
    # [p for p in sampled_points if p.is_point]
    return regressor.fit_predict(sampled_points)