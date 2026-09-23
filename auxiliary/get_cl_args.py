import sys

def get_args():
	'''
	Returns command line arguments for Lx, Ly, alpha, gamma, runs and seed
	'''
	if len(sys.argv) != 8:
		print("6 arguments are expected: Lx, Ly, alpha, gamma, runs and seed")
		exit(-1)
	args = sys.argv
	return int(args[2]), int(args[3]), int(args[4]), float(args[5]), int(args[6]), int(args[7])
