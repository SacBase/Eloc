"""Generation of random spin state configurations for local energy calculations."""

import numpy as np
from get_cl_args import get_args

def random_states(N, runs, seed=0):
    rng = np.random.default_rng(seed)
    return (rng.integers(low=0, high=2, size=(runs, N)) * 2 - 1).astype(np.float64)

if __name__ == "__main__":
    Lx, Ly, alpha, _, runs, seed = get_args()
    N = Lx * Ly

    states = random_states(N, runs, seed=seed)

    np.savetxt(f"data/states/states_{runs}x{N}.csv", states, fmt="%.0f", delimiter=",")

