import sys

def get_args():
	'''
	Returns command line arguments for Lx, Ly, alpha, gamma, runs and seed
	'''
	if len(sys.argv) != 7:
		print("6 arguments are expected: Lx, Ly, alpha, gamma, runs and seed")
		print("got:", sys.argv[1:])
		exit(-1)
	args = sys.argv
	return int(args[1]), int(args[2]), int(args[3]), float(args[4]), int(args[5]), int(args[6])