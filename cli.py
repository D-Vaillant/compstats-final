# cli.py
import argparse
from learning.learner import calculate_error, KernelRegressor


# Inputs: bandwidth, kernel type.
# Also inputs: equation to calculate ground truth points and MSE.