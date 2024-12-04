#!/usr/bin/env python3
# cli.py
import argparse
import sys
from learning.learner import calculate_error, KernelRegressor
from learning.graph import generate_points

# Inputs: bandwidth, kernel type.
# Also inputs: equation to calculate ground truth points and MSE.


N = 1000  # Hardcoded... FOR NOW

def make_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument('A', type=float, help='Amplitude modifier for X')
    parser.add_argument('a', type=float, help='Frequency modifier for X')
    parser.add_argument('B', type=float, help='Amplitude modifier for Y')
    parser.add_argument('b', type=float, help='Frequency modifier for Y')
    parser.add_argument('--delta', default=0, metavar='δ', type=float, help='Frequency offset for X')
    parser.add_argument('--noise', default=0, metavar='ϵ', type=float, help='Variance of gaussian noise in sampling')
    parser.add_argument('--kernel', choices=['normal', 'quartic', 'parabolic', 'cosine'],
                        default='normal', help='Kernel to use for regression')
    parser.add_argument('-bwx', '--bandwidth_x', default=0.2, type=float, help='Bandwidth for X regressor')
    parser.add_argument('-bwy', '--bandwidth_y', default=0.2, type=float, help='Bandwidth for Y regressor')
    parser.add_argument('--x', action='store_true', help='Prints results in scriptable form.')
    parser.add_argument('--header', action='store_true', help='Includes the header.')
    return parser


if __name__ == "__main__":
    parser = make_argparse()
    args = parser.parse_args()
    ground_truth, sampled_points = generate_points(args.A, args.a, args.B, args.b, args.delta,
                                                   n_sampled=50, noise=args.noise, n_points=N)
    regressor = KernelRegressor(args.bandwidth_x, args.bandwidth_y, args.kernel)
    fitted_points = regressor.fit_predict(sampled_points, num_output_points=N)
    # A bit hacky, sorry.
    args.mse = calculate_error(ground_truth, fitted_points)

    # Human readable.
    if not args.x:
        # TODO: Create `format_equation` that makes this look nicer.
        print(f"Parameters: f(t) = ({args.A}*sin({args.a} * t + {args.delta}), {args.B}*sin({args.b} * t))")
        print(f"Sample variance is {args.noise}. {args.kernel} kernel, bandwidth_x={args.bandwidth_x}, bandwidth_y={args.bandwidth_y}")
        print(f"MSE = {args.mse}")
    else:
        # Scriptable (for CSV).
        header = [action.dest for action in parser._actions if (action.dest not in ('help', 'x'))]
        header.append('mse')
        if args.header:
            print(','.join(header))

        # TODO: How many decimals do we want?
        row = [str(getattr(args, col)) for col in header]
        row.append(f"{args.mse}")
        print(','.join(row))
    