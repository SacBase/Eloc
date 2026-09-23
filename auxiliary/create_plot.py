import matplotlib.pyplot as plt
import numpy as np
import os

def load_result(file_name, data_dir="results"):
	return np.genfromtxt(
		os.path.join(data_dir, file_name), delimiter=",", dtype=np.float64
	)

def toString(arr):
	ret = []
	for x in arr:
		ret.append(str(x))
	return ret

if __name__ == "__main__":

	langs = ["sac", "python"]
	sizes = [256]
	labels = []
	nruns = 1000
	q = 0.025
	bot = int(np.floor(nruns * q))
	top = int(np.ceil(nruns * (1 - q)))

	fig, ax = plt.subplots()
	nr_langs = len(langs)
	x_labels = toString(sizes)
	ind = np.arange(len(sizes))
	width = 0.7 / nr_langs

	for s in sizes:
		labels.append(str(s))

	for i, lang in enumerate(langs):
		medians = []
		err = [[],[]]
		for s in sizes:
			data = load_result(f"{lang}_{s}.csv")
			data = np.sort(data)[bot:top]
			medians.append(np.median(data))
			
			err[0].append(medians[-1] - np.min(data))
			err[1].append(np.max(data) - medians[-1])
		print(medians)
		ax.bar(ind - nr_langs*width/2 + (i+0.5)*width, medians, width, yerr=err, label=lang)

	ax.set_ylabel("runtime (s)")
	ax.set_title(f"Runtimes of Eloc (N={nruns})")
	ax.set_xticks(ind)
	ax.set_xticklabels(x_labels)
	ax.legend()

	fig.tight_layout()

	plt.savefig("results/plt.png")


