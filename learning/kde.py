# # Bird species.
# Cyanocitta cristata, Blue jay
# Baeolophus bicolor, Tufted titmouse
# Sitta carolinensis, White-breasted nuthatch
# Melanerpes carolinus, Red-bellied woodpecker

import numpy as np
from scipy.linalg import sqrtm, det, inv
from typing import List, Tuple, Dict
from learning.graph import Point
import functools

rng = np.random.default_rng()


def ucv_loss(H, samples):
    # Assumes normal kernel with mean of 0 and covariance of identity.
    samples = np.asarray(samples)
    n = len(samples)
    d = samples.shape[1]

    phis = lambda x: phi_h(2*H)(x) - 2*phi_h(H)(x)
    output = 0
    for i, X_i in enumerate(samples):
        for j, X_j in enumerate(samples):
            if i != j: 
                output += phis(X_i - X_j)
    output /= (n * (n-1))
    output += (1/n) * (4*np.pi)**(-d/2) * det(H)**(-0.5)
    return float(output)


def normal_kernel(x):
    # Multivariate. Assuming mean = 0, covariance = identity.
    x = np.asarray(x)
    d = len(x)
    if x.ndim == 1:
        x = np.array(x).reshape(-1, 1)
    d = x.shape[1]

    norms = np.sum(x * x, axis=1)
    return (np.exp(-0.5 * norms) / ((2 * np.pi) ** (d/2)))


def phi_h(H) -> callable:
    H_inv_sqrt = inv(sqrtm(H))
    det_H = det(H)

    def h_kernel(x: np.ndarray) -> np.ndarray:
        if x.ndim == 1:
            x = np.array(x).reshape(-1, 1)
        tr_x = x @ H_inv_sqrt
        return (det_H**(-0.5) * normal_kernel(tr_x))
    
    return h_kernel


class MultidimensionalKDE():
    def __init__(self, samples: np.array,
                 bandwidth_matrix: np.array):
        self.samples = np.asarray(samples)
        self.H = bandwidth_matrix
        self.n = len(self.samples)
        self.K = phi_h(self.H)

    def kde(self, s):
        s = np.asarray(s)
        if s.ndim == 1:
            s = s.reshape(1, -1)
            
        # Some black magic to vectorize the operations.
        # (num_eval, dim) - (num_samples, dim) -> (num_eval, num_samples, dim)
        diffs = s[:, np.newaxis, :] - self.samples[np.newaxis, :, :]
        reshaped_diffs = diffs.reshape(-1, diffs.shape[-1])  # (num_eval*num_samples, dim)
        kernel_values = self.K(reshaped_diffs)  # Get kernels of everything, and...
        kernel_values = kernel_values.reshape(len(s), self.n)  # (num_eval, num_samples)
        # And then sum up the kernel applications for each point we're evaluating.
        return np.sum(kernel_values, axis=1) / self.n


class WeightedMultidimensionalKDE():
    def __init__(self, samples: np.array,
                 weights: np.array,
                 bandwidth_matrix: np.array):
        self.samples = np.asarray(samples)
        self.weights = np.asarray(weights)
        self.H = bandwidth_matrix
        self.n = len(self.samples)
        self.total_weights = sum(weights)
        self.K = phi_h(self.H)

    def kde(self, s):
        s = np.asarray(s)
        if s.ndim == 1:
            s = s.reshape(1, -1)
            
        # Some black magic to vectorize the operations.
        # (num_eval, dim) - (num_samples, dim) -> (num_eval, num_samples, dim)
        diffs = s[:, np.newaxis, :] - self.samples[np.newaxis, :, :]
        reshaped_diffs = diffs.reshape(-1, diffs.shape[-1])  # (num_eval*num_samples, dim)
        kernel_values = self.K(reshaped_diffs)  # Get kernels of everything, and...
        kernel_values = kernel_values.reshape(len(s), self.n)  # (num_eval, num_samples)
        # And then sum up the kernel applications for each point we're evaluating.
        return np.sum(kernel_values * self.weights, axis=1) / self.total_weights
    

class SpaceTimeKDE():
    def __init__(self, space_samples: np.array,
                 time_samples: np.array,
                 bandwidth_matrix: np.array,
                 temporal_bandwidth: float):
        self.space_samples = np.asarray(space_samples)
        self.times = np.asarray(time_samples).reshape(-1, 1)
        self.H = bandwidth_matrix
        self.h_t = temporal_bandwidth
        self.n = len(self.samples)
        self.K_s = phi_h(self.H)
        self.K_t = phi_h([[temporal_bandwidth]])

    def kde(self, s, t):
        s = np.asarray(s)
        t = np.asarray(t)
        
        if s.ndim == 1:
            s = s.reshape(1, -1)
        if t.ndim == 0:
            t = t.reshape(1)

        # See above re: black magic.
        space_diffs = s[:, np.newaxis, :] - self.spaces[np.newaxis, :, :]
        time_diffs = t[:, np.newaxis, np.newaxis] - self.times[np.newaxis, :, :]
        
        reshaped_space_diffs = space_diffs.reshape(-1, space_diffs.shape[-1])
        reshaped_time_diffs = time_diffs.reshape(-1)
        
        space_kernel = self.K_s(reshaped_space_diffs)
        time_kernel = self.K_t(reshaped_time_diffs)
            
        space_kernel = space_kernel.reshape(len(s), self.n)
        time_kernel = time_kernel.reshape(len(t), self.n)
        
        # Multiply kernels and sum
        return np.sum(space_kernel * time_kernel, axis=1) / self.n


def fit_and_calculate(sampled_points: Dict[str, np.ndarray],
                      bandwidth_matrix=None):
    # Extract coordinates from sampled points
    Xs = sampled_points['x']
    Ys = sampled_points['y']
    Ts = sampled_points['t']
    Zs = sampled_points['z']
    spatial_data = np.column_stack((Xs, Ys))

    if bandwidth_matrix is None:
        bandwidth_matrix = 0.2 * np.eye(spatial_data.ndim)

    KDE = WeightedMultidimensionalKDE(spatial_data,
                                      weights=Zs,
                                      bandwidth_matrix=0.2*np.eye(spatial_data.ndim))
    # Prediction part.
    x_min = min(Xs)
    x_max = max(Xs)
    y_min = min(Ys)
    y_max = max(Ys)

    lats = np.linspace(x_min, x_max, num=100)  # 1-degree steps
    lons = np.linspace(y_min, y_max, num=100)  # 1-degree steps

    lat_grid, lon_grid = np.meshgrid(lats, lons)
    coords = np.stack((lat_grid.flatten(), lon_grid.flatten()), axis=1)

    evaluations = KDE.kde(coords)
    return np.array([{'lat': lat, 'lon': lon, 'z': e} for (lat, lon), e in zip(coords, evaluations)])


