# ELoc

# Eloc reference implementation

Neural Quantum States (NQS) is a method to find the ground state (lowest energy
state) of a quantum system. NQS uses a neural network (here, a restricted
Boltzmann machine, RBM) to represent the quantum many-body wavefunction
$\psi(s)$ of a quantum system, where $s$ is a spin configuration, see [Neural
Quantum States](Neural%20Quantum%20States.md).

A key step in NQS is computing the **local energy** $E_\text{loc}(s)$ of a spin
configuration $s$ sampled from $|\psi(s)|^2$. A small reference implementation
of the **local energy (Eloc)** calculation used in Neural Quantum State (NQS)
variational Monte Carlo is provided and pseudocode is described below.

## What is the local energy/Eloc?

In variational Monte Carlo, a trial wavefunction $\psi_M$ (here, a
restricted Boltzmann machine, RBM) is evaluated by sampling spin
configurations $s$ from $|\psi_M(s)|^2$ and averaging the **local energy**

$$
E_\text{loc}(s) = \frac{\langle s | \hat{H} | \psi_M \rangle}{\langle s | \psi_M \rangle}
= \sum_{s'} \langle s | \hat{H} | s' \rangle \, \frac{\psi_M(s')}{\psi_M(s)}.
$$

$\hat H$ is sparse (a sum of local terms), so this sum over exponentially
many $s'$ reduces to a handful of terms. This repo covers the **Heisenberg
exchange term** on a 2D square lattice,

$$
\hat{H}_\text{ex} = \sum_{\langle i,j \rangle} J_{ij}\,\hat{\mathbf S}_i \!\cdot\! \hat{\mathbf S}_j,
$$

which, after applying the Marshall sign rule, contributes a diagonal piece
plus one off-diagonal term per bond where the two spins differ:

$$
E_\text{loc}(s) = \sum_{\langle i,j\rangle} s_i s_j
\;-\; 2\sum_{\langle i,j\rangle} \delta_{s_i,-s_j}\, e^{\log\psi(s') - \log\psi(s)},
$$

where $s'$ is $s$ with the two spins on bond $(i,j)$ flipped and $\langle
i,j\rangle$ runs over all bonds. So computing $E_\text{loc}$ for one
configuration means, for every "flippable" bond, evaluating the wavefunction at
the flipped configuration and comparing it to the wavefunction at $s$. This is
the loop `eloc_naive`/`eloc_lookup_table` implement in `eloc.py`.

More about the derivation of the local energy in NQS is in [Eloc in NQS](Eloc%20in%20NQS.md) and more about Neural Quantum States is in [Neural Quantum States](Neural%20Quantum%20States.md).

## The RBM ansatz

The RBM wavefunction is

$$
\psi(s) = \exp\!\left[\tfrac12 \sum_{h=1}^{M} \log\big(2\cosh(\theta_h)\big)\right],
\qquad \theta_h = b_h + \sum_i W_{ih}\, s_i,
$$

with $M = \alpha \cdot N_\text{spins}$ hidden units. Two ways to get
$\log\psi(s')$ for a flipped configuration:

- **Naive** (`eloc_naive`): recompute $\theta'$ from scratch, i.e. a full
  $s' \cdot W$ matrix-vector product. Cost: $O(N_\text{bonds} \cdot N_\text{spins} \cdot M)$.
- **Lookup table** (`eloc_lookup_table`): $\theta$ for the *unflipped* $s$
  is computed once; a bond flip only changes two spins, so
  $\theta'_h = \theta_h - 2 W_{ih} s_i - 2 W_{jh} s_j$ updates every hidden
  unit in $O(M)$ instead of $O(N_\text{spins} \cdot M)$. Cost:
  $O(N_\text{bonds} \cdot M)$ total.

The lookup-table method is the implementation of choice because of the improved
scaling win.

## Algorithm for computing $E_\text{loc}(s)$ for a single configuration $s$:

1. Initialize $\theta_h$.
2. Calculate $\log\psi(s)$ from $\theta_h$ by $\log\psi(s) = \gamma \sum_{h=1}^{M} \log\big(2\cosh(\theta_h)\big)$.
3. $E_\text{loc} = 0$.
4. Loop over all bonds $(i,j)$, and if $s_i \neq s_j$:
   1. Flip the two spins $s_i$ and $s_j$, which gives $\theta'_h = \theta_h - 2 W_{ih} s_i - 2 W_{jh} s_j$.
   2. Calculate $\log\psi(s') = \gamma \sum_{h=1}^{M} \log\big(2\cosh(\theta'_h)\big)$.
   3. $E_\text{loc} = E_\text{loc} -2 \exp\big(\log\psi(s') - \log\psi(s)\big)$.
5. Calculate the diagonal part: loop over all bonds $(i,j)$, $E_\text{loc} = E_\text{loc} + s_i \cdot s_j$.

Note that we use $\gamma=0.5$ here. 


# Usage

## Preperations

Install required python libraries:
```
pip install -r requirements.txt
```

Generate random states:
```
python auxiliary/generate_states.py
```

## Running files

### Python
```
python eloc.py
```

### Sac
Running sac sequentially:
```
sac2c eloc.sac
./a.out
```

Running sac multi-threaded using $N$ threads:
```
sac2c -tmt_pth eloc.sac
./a.out -mt N
```
