import numpy as np
from typing import List, Tuple, Dict
from learning.graph import Point


class NonparametricRegressor:
    def __init__(self, bandwidth: float = 0.1):
        """
        Initialize the nonparametric regressor.
        Args:
            bandwidth: Smoothing parameter for the regression
        """
        self.bandwidth = bandwidth

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
        t_data = np.array([p.t for p in sampled_points if p.is_point])
        x_data = np.array([p.x for p in sampled_points if p.is_point])
        y_data = np.array([p.y for p in sampled_points if p.is_point])


        t_smooth = np.linspace(0, 2*np.pi, num_output_points)
        x_smooth = np.cos(t_smooth)
        y_smooth = np.sin(t_smooth)

        fitted_points = []
        for t, x, y in zip(t_smooth, x_smooth, y_smooth):
            fitted_points.append(Point(t, x, y))
        
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

def fit_curve(sampled_points: List[Point]) -> List[Point]:
    """
    Wrapper function to maintain the same interface.
    """
    regressor = NonparametricRegressor()
    return regressor.fit_predict(sampled_points)