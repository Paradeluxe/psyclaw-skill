import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

fig, ax = plt.subplots()

def rounded_rect(x, y, width, height, radius):
    verts = [
        (x + radius, y),
        (x + width - radius, y),
        (x + width, y + radius),
        (x + width, y + height - radius),
        (x + width - radius, y + height),
        (x + radius, y + height),
        (x, y + height - radius),
        (x, y + radius),
        (x + radius, y),
        (x + radius, y),
    ]
    codes = [Path.MOVETO, Path.LINETO, Path.QUADRATIC, Path.LINETO,
             Path.QUADRATIC, Path.LINETO, Path.QUADRATIC, Path.LINETO,
             Path.QUADRATIC, Path.CLOSEPOLY]
    return Path(verts, codes)

x, y, w, h, r = 0.2, 0.2, 0.6, 0.6, 0.1
path = rounded_rect(x, y, w, h, r)
patch = patches.PathPatch(path, linewidth=2, edgecolor='black', facecolor='lightblue')
ax.add_patch(patch)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect('equal')
plt.show()
