"""Splits the real observed RBM weights into two seperate files. 
   This requires a full pass over the Ising file, but subsequent uses of 
   the weight data only have to read ~2/9ths of the file. 
	
   File "weights_{N}_{alpha}_ti_J.csv" will contain the weights used in the E_loc calculations ([M:M+N, :M])
   File "weights_{N}_{alpha}_ti_z.csv" will contain the remaining non-zero block of data ([:M, M:M+N])
   File "weights_{N}_{alpha}_ti_h.csv" will be a copy of the "Ising_{N}_{alpha}_ti_h.cvs" file
"""

import numpy as np
from get_cl_args import get_args

if __name__ == "__main__":
	Lx, Ly, alpha, _, runs, _ = get_args()
	N = Lx * Ly
	M = N * alpha

	W_full = np.genfromtxt(f"data/weights/Ising_{N}_{alpha}_ti_J.csv", delimiter=",", dtype=np.float64)
	b      = np.genfromtxt(f"data/weights/Ising_{N}_{alpha}_ti_h.csv", delimiter=",", dtype=np.float64)

	W = W_full[M:M + N, :M].copy()
	z = W_full[:M, M:M + N].copy()

	np.savetxt(f"data/weights/weights_{N}_{alpha}_ti_J.csv", W, fmt="%.18e", delimiter=",")
	np.savetxt(f"data/weights/weights_{N}_{alpha}_ti_z.csv", z, fmt="%.18e", delimiter=",")
	np.savetxt(f"data/weights/weights_{N}_{alpha}_ti_h.csv", b, fmt="%.18e", delimiter=",")

