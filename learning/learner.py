import numpy as np
from typing import List, Tuple, Dict
from learning.graph import Point


class KernelRegressor:
    def __init__(self,
                 bandwidth_x: float = 0.1,
                 bandwidth_y: float = 0.1,
                 kernel_choice: str = 'normal'):
        """
        Initialize the nonparametric regressor.
        Args:
            bandwidth: Smoothing parameter for the regression
            kernel_choice: Chooses the kernel.
        """
        self.bwx = bandwidth_x
        self.bwy = bandwidth_y
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

        t_smooth = np.linspace(0, 2*np.pi, num_output_points)

        fitted_points = []
        for i, t in enumerate(t_smooth):
            xweights = self.K((t - t_data) / self.bwx)
            yweights = self.K((t - t_data) / self.bwy)

            # if np.sum(xweights) == 0:
            #     print(xweights)
            # if np.sum(yweights) == 0:
            #     print(yweights)
            est_x = np.sum(x_data * xweights) / np.sum(xweights)
            est_y = np.sum(y_data * yweights) / np.sum(yweights)
            fitted_points.append(Point(t, est_x, est_y))

        return fitted_points

def fit_curve(sampled_points: List[Point],
              bandwidth_x: float = 0.1,
              bandwidth_y: float = 0.1,
              kernel: str = 'normal') -> List[Point]:
    """
    Wrapper function to maintain the same interface.
    """
    regressor = KernelRegressor(bandwidth_x=bandwidth_x,
                                bandwidth_y=bandwidth_y,
                                kernel_choice=kernel)
    # [p for p in sampled_points if p.is_point]
    return regressor.fit_predict(sampled_points)


def calculate_error(ground_truth: List[Point],
                    fitted_points: List[Point]) -> float:
    # This requires that we have the same amount of points in ground_truth and fitted_points.
    # This is because the backend actually doesn't know the function at all. It just has the graph of it.
    # This could be fixed in other ways, but I'm doing the hack of enforcing this.
    try:
        assert(len(ground_truth) == len(fitted_points))
    except AssertionError:
        return -1  # Error code: Unequal lengths of ground_truth and fitted_points.
    # print(f"Ground truth length: {len(ground_truth)}")
    # print(f"Fitted points length: {len(fitted_points)}")
    
    gt_array = np.array([(p.x, p.y) for p in ground_truth])
    fit_array = np.array([(p.x, p.y) for p in fitted_points])
    
    differences = gt_array - fit_array
    # assert(len(ground_truth) == len(fitted_points))
    # differences = np.array([(p.x, p.y) for p in ground_truth]) - np.array([(p.x, p.y) for p in fitted_points])
    return np.mean(np.sum(differences ** 2, axis=1))