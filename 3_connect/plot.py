import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

mem_pot = pd.read_csv('MemPot.dat', delim_whitespace=True, names=['time', 'neu1', 'neu2'])

plt.style.use('seaborn')
fig, axes = plt.subplots(2, sharex=True, sharey=False)
axes[0].plot(mem_pot['time'] * 1000, mem_pot['neu1'] * 1000, label='Presynaptic', linewidth=1.4)
axes[1].plot(mem_pot['time'] * 1000, mem_pot['neu2'] * 1000, color='r', label='Postsynaptic', linewidth=1.4)
axes[0].legend(loc='lower right', prop={'size': 12})
axes[1].legend(loc='lower right', prop={'size': 12})

plt.xlabel('Time (ms)', size=14)
plt.ylabel('Membrane Potential (mV)', position=(0, 1), size=14)
fig.subplots_adjust(hspace=0.015)

plt.savefig('MemPot.png', format='png', bbox_inches='tight', dpi=100)
plt.show()
