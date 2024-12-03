import numpy as np
import matplotlib.pyplot as plt
from learning.graph import Point
from learning.learner import NonparametricRegressor
from typing import List, Tuple

def generate_toy_data(num_points: int = 1000, 
                     num_samples: int = 20, 
                     noise_level: float = 0.1) -> Tuple[List[Point], List[Point]]:
    """
    Generate toy Lissajous data with noise.
    Returns both the ground truth and noisy sampled points.
    """
    # Generate ground truth
    t = np.linspace(0, 2*np.pi, num_points)
    A, a = 3.0, 2.0
    B, b = 2.0, 3.0
    phase = np.pi/2
    
    x = A * np.cos(a * t)
    y = B * np.sin(b * t + phase)
    
    # Create ground truth points
    ground_truth = [
        Point(t=float(t[i]), x=float(x[i]), y=float(y[i]), 
              is_point=False, color='')
        for i in range(num_points)
    ]
    
    # Generate noisy samples
    sample_indices = np.linspace(0, len(t)-1, num_samples, dtype=int)
    sampled_points = []
    
    for idx in sample_indices:
        noisy_x = x[idx] + np.random.normal(0, noise_level)
        noisy_y = y[idx] + np.random.normal(0, noise_level)
        color = f'#{np.random.randint(0, 0xFFFFFF):06x}'
        
        sampled_points.append(
            Point(t=float(t[idx]), x=float(noisy_x), y=float(noisy_y),
                  is_point=True, color=color)
        )
    
    return ground_truth, sampled_points

def plot_results(ground_truth: List[Point], 
                sampled_points: List[Point], 
                predicted: List[Point]):
    """
    Create a plot comparing ground truth, samples, and prediction.
    """
    plt.figure(figsize=(12, 8))
    
    # Plot ground truth
    gt_x = [p.x for p in ground_truth]
    gt_y = [p.y for p in ground_truth]
    plt.plot(gt_x, gt_y, 'b-', label='Ground Truth', alpha=0.5)
    
    # Plot predicted curve
    pred_x = [p.x for p in predicted if not p.is_point]
    pred_y = [p.y for p in predicted if not p.is_point]
    plt.plot(pred_x, pred_y, 'r--', label='Predicted', alpha=0.7)
    
    # Plot sampled points
    sample_x = [p.x for p in sampled_points]
    sample_y = [p.y for p in sampled_points]
    plt.scatter(sample_x, sample_y, c='g', label='Samples')
    
    plt.title('Nonparametric Regression Results')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def main():
    # Generate toy data
    ground_truth, sampled_points = generate_toy_data(
        num_points=1000,
        num_samples=20,
        noise_level=0.1
    )
    
    # Create and run regressor
    regressor = NonparametricRegressor(bandwidth=0.1)
    predicted_points = regressor.fit_predict(sampled_points)
    
    plot_results(ground_truth, sampled_points, predicted_points)
    
    gt_points = np.array([(p.x, p.y) for p in ground_truth])
    pred_points = np.array([(p.x, p.y) for p in predicted_points if not p.is_point])
    mse = np.mean(np.sum((gt_points - pred_points[:len(gt_points)])**2, axis=1))
    print(f"Mean Squared Error: {mse:.6f}")

if __name__ == "__main__":
    main()