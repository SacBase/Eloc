"""Reference implementation of the local-energy (Eloc) kernel for NQS.

Two versions of the same quantity are provided:

- ``eloc_naive``: recomputes the RBM wavefunction from scratch for every bond
  flip. This is the easy-to-read, easy-to-verify baseline.
- ``eloc_lookup_table``: reuses theta and updates only the two entries that
  change per bond flip.

Both take a spin configuration `s` (+-1 valued, shape (N,)), the RBM weights `W`
(shape (N, M)) and biases `b` (shape (M,)) with M = alpha*N, and a `bonds` array
(shape (nbonds, 2)) of 0-indexed site pairs. They return the local energy of the
Heisenberg exchange term only, in the same units as the couplings baked into
`bonds`/`s` (i.e. un-normalized; divide by N*4 to compare across system sizes,
see README.md).

Notation, matching README.md symbol-for-symbol:
    s, s_prime   spin configuration s and the bond-flipped s' N, M number of
    spins, number of hidden units (M = alpha*N) W, b         RBM weights W_ih
    and biases b_h theta        pre-activation theta_h = b_h + sum_i W_ih s_i
    theta_prime  theta' for s' (only differs from theta on flipped bonds)
    delta_theta  theta - theta', i.e. the two-term correction per bond flip
    logpsi_s, logpsi_s_prime   log psi(s), log psi(s') E_loc the local energy
    E_loc(s)
"""

import os
import time

import numpy as np
from numba import njit


@njit
def logpsi(s, W, b, gamma=0.5):
    """log(psi(s)) for the RBM ansatz, along with theta and its activation.

    theta_h = b_h + sum_i W_ih * s_i
    log psi(s) = gamma * sum_h log(2 cosh(theta_h))
    """
    M = W.shape[1]
    theta = np.zeros(M, dtype=np.float64)
    for h in range(M):
        acc = 0.0
        for i in range(s.shape[0]):
            acc += s[i] * W[i, h]
        theta[h] = acc + b[h]

    activation = 2 * np.cosh(theta)
    logpsi_s = gamma * np.sum(np.log(activation))
    return logpsi_s, theta, activation


@njit
def eloc_naive(s, bonds, W, b, gamma=0.5):
    """Local energy via full re-evaluation of psi(s') per bond flip.

    O(nbonds * N * M): for every bond, the whole matrix-vector product
    s' @ W is recomputed from scratch inside logpsi.
    """
    logpsi_s, _, _ = logpsi(s, W, b, gamma=gamma)

    E_loc = 0.0
    for k in range(bonds.shape[0]):
        i, j = bonds[k, 0], bonds[k, 1]
        E_loc += s[i] * s[j]

        if s[i] != s[j]:
            s_prime = s.copy()
            s_prime[i] = -s_prime[i]
            s_prime[j] = -s_prime[j]
            logpsi_s_prime, _, _ = logpsi(s_prime, W, b, gamma=gamma)
            E_loc -= 2 * np.exp(logpsi_s_prime - logpsi_s)

    return E_loc


@njit
def eloc_lookup_table(s, alpha, bonds, W, b, gamma=0.5):
    """Local energy via incremental updates of theta (lookup-table method).

    O(nbonds * M): theta is computed once; each bond flip only updates the
    two terms of theta that depend on the flipped sites, so a flip costs
    O(M) instead of O(N * M).

    """
    N = s.shape[0]
    M = N * alpha
    logpsi_s, theta, _ = logpsi(s, W, b, gamma=gamma)
    W_T = W.transpose()

    E_loc = 0.0
    for k in range(bonds.shape[0]):
        i, j = bonds[k, 0], bonds[k, 1]
        E_loc += s[i] * s[j]
        if s[i] != s[j]:
            delta_theta = np.zeros(M, dtype=np.float64)
            for h in range(M):
                delta_theta[h] = 2 * W_T[h, i] * s[i] + 2 * W_T[h, j] * s[j]
            theta_prime = theta - delta_theta
            activation_prime = 2 * np.cosh(theta_prime)
            logpsi_s_prime = gamma * np.sum(np.log(activation_prime))
            E_loc -= 2 * np.exp(logpsi_s_prime - logpsi_s)

    return E_loc


def square_lattice_bonds(Lx, Ly, periodic=True):
    """Nearest-neighbour bonds of an Lx*Ly square lattice, 0-indexed sites.

    Site (x, y) is flattened to index y * Lx + x (x fastest-varying), and
    bonds are returned as all x-bonds followed by all y-bonds. This matches
    UltraFast.jl's `Lattice.LatticeConfig` (`InitLattice_` in
    `Lattice/Heisenberg_lattice.jl`) for the periodic, Lx > 2 and Ly > 2
    case.
    """
    def index(x, y):
        return y * Lx + x

    bonds_x = []
    for y in range(Ly):
        for x in range(Lx):
            if periodic or x + 1 < Lx:
                bonds_x.append((index(x, y), index((x + 1) % Lx, y)))

    bonds_y = []
    for y in range(Ly):
        for x in range(Lx):
            if periodic or y + 1 < Ly:
                bonds_y.append((index(x, y), index(x, (y + 1) % Ly)))

    return np.array(bonds_x + bonds_y, dtype=np.int64)


def random_rbm(N, alpha, seed=0, scale=0.001):
    """A random RBM (W, b) with the shapes eloc expects, for smoke tests
    and benchmarking."""
    rng = np.random.default_rng(seed)
    M = N * alpha
    W = rng.normal(scale=scale, size=(N, M))
    b = rng.normal(scale=scale, size=M)
    return W, b

def random_state(N, seed=0):
    rng = np.random.default_rng(seed)
    return (rng.integers(low=0, high=2, size=N) * 2 - 1).astype(np.float64)

def random_states(N, runs, seed=0):
    rng = np.random.default_rng(seed)
    return (rng.integers(low=0, high=2, size=(runs, N)) * 2 - 1).astype(np.float64)

def load_trained_rbm(N, alpha, data_dir="data/weights"):
    """Load a real, trained RBM (W, b) -- a physically meaningful
    (state, W, b) input to check eloc against, not just a random one.

    Reads `Ising_{N}_{alpha}_ti_J.csv`/`..._ti_h.csv` and applies the same
    slice as the original numba_eloc.py: the raw CSVs store the full
    network parameters, and only a (N, M) block of the weight matrix and
    the first M entries of the bias vector are the RBM weights/biases
    eloc.py expects (M = alpha*N).
    """
    M = alpha * N
    W_full = np.genfromtxt(
        os.path.join(data_dir, f"weights_{N}_{alpha}_ti_J.csv"), delimiter=",", dtype=np.float64
    )
    b_full = np.genfromtxt(
        os.path.join(data_dir, f"weights_{N}_{alpha}_ti_h.csv"), delimiter=",", dtype=np.float64
    )
    W = W_full[:N, :M].copy()
    b = b_full[:M].copy()
    return W, b

def load_states(N, runs, data_dir="data/states"):
    return np.genfromtxt(
        os.path.join(data_dir, f"states_{runs}x{N}.csv"), delimiter=",", dtype=np.float64
    )

if __name__ == "__main__":
    Lx, Ly, alpha = 16, 16, 2
    N = Lx * Ly
    runs = 1000
    seed = 0

    bonds = square_lattice_bonds(Lx, Ly)
    try:
        W, b = load_trained_rbm(N, alpha)
        print(f"using trained weights from data/weights/weights_{N}_{alpha}_ti_*.csv")
    except OSError:
        W, b = random_rbm(N, alpha, seed=seed)
        print("data/weights not found -- using a random RBM instead")

    states = load_states(N, runs)

    results = np.zeros(runs)
    rts = np.zeros(runs)
    total_rt = 0

    for i in range(runs):
        s = states[i]

        start = time.time()
        e_lookup = eloc_lookup_table(s, alpha, bonds, W, b) / (N * 4)
        t_lookup = time.time() - start
        total_rt += t_lookup

        print(
            f"run={i}  eloc={e_lookup:.6f} ({t_lookup * 1e3:.3f} ms)"
        )
        
        results[i] = e_lookup
        rts[i] = t_lookup

    print(f"total runtime:   {total_rt:.6f} seconds")
    print(f"average runtime: {total_rt/runs:.6f}")
    print(f"summed eloc:     {sum(results):.6f}")

    np.savetxt(f"results/python_{N}.csv", rts, fmt="%.6f", delimiter=",")