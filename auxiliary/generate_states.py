"""Generation of random spin state configurations for local energy calculations."""

import numpy as np

def random_states(N, runs, seed=0):
    rng = np.random.default_rng(seed)
    return (rng.integers(low=0, high=2, size=(runs, N)) * 2 - 1).astype(np.float64)

if __name__ == "__main__":
    Lx = 16
    Ly = 16
    N = Lx * Ly
    runs = 1000
    seed = 0

    states = random_states(N, runs, seed=seed)

    np.savetxt(f"data/states/states_{runs}x{N}.csv", states, fmt="%.0f", delimiter=",")

