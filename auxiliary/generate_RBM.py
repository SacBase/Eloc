"""Generation of random RBM for local energy calculations."""

import numpy as np
from get_cl_args import get_args

def random_weights(N, alpha, seed=0, scale=0.001):
    rng = np.random.default_rng(seed)
    M = N * alpha
    W = rng.normal(scale=scale, size=(N, M))
    return W

def random_bias(N, alpha, seed=0, scale=0.001):
    rng = np.random.default_rng(seed)
    M = N * alpha
    b = rng.normal(scale=scale, size=M)
    return b

if __name__ == "__main__":
    Lx, Ly, alpha, _, runs, seed = get_args()

    N = Lx * Ly

    W = random_weights(N, alpha, seed=seed)
    b = random_bias(N, alpha, seed=seed)


    np.savetxt(f"data/weights/weights_{N}_{alpha}_ti_J.csv", W, fmt="%.18e", delimiter=",")
    np.savetxt(f"data/weights/weights_{N}_{alpha}_ti_h.csv", b, fmt="%.18e", delimiter=",")

