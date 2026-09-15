# ELoc

This repository contains files used for the benchmarking of local energy computation implementations.

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
