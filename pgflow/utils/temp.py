import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm

# Example data: replace these with your actual xy points and velocities
xy = np.column_stack(
    (np.linspace(0, 3 * np.pi, 500), np.sin(np.linspace(0, 3 * np.pi, 500)))
)
velocities = np.abs(np.cos(0.5 * (xy[:-1, 0] + xy[1:, 0])))  # Example velocities

# Create line segments
segments = np.concatenate([xy[:-1, None], xy[1:, None]], axis=1)

fig, axs = plt.subplots(2, 1, sharex=True, sharey=True)

# Continuous coloring based on velocity
norm = plt.Normalize(velocities.min(), velocities.max())
lc = LineCollection(segments, cmap="viridis", norm=norm)
lc.set_array(velocities)
lc.set_linewidth(2)
line = axs[0].add_collection(lc)
fig.colorbar(line, ax=axs[0])

# Discrete coloring based on velocity
cmap = ListedColormap(["r", "g", "b"])
norm = BoundaryNorm(
    [-1, -0.5, 0.5, 1], cmap.N
)  # Adjust these boundaries to match your velocity ranges
lc = LineCollection(segments, cmap=cmap, norm=norm)
lc.set_array(velocities)
lc.set_linewidth(2)
line = axs[1].add_collection(lc)
fig.colorbar(line, ax=axs[1])

axs[0].set_xlim(xy[:, 0].min(), xy[:, 0].max())
axs[0].set_ylim(xy[:, 1].min(), xy[:, 1].max())
plt.show()
