import matplotlib.pyplot as plt
import numpy as np
from process_data import extract_features

features=extract_features('data/LA_net.txt')
capacities=[line[1] for line in features]
med=max(capacities)
print med
