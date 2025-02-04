#!/usr/bin/env python
"""
Produces PNGs of all available colormaps in Matplotlib.

Written  Matthias Cuntz, Dec 2020

"""
import numpy as np
import matplotlib as mpl
# PNG
mpl.use('Agg')  # set directly after import matplotlib
# PDF
# matplotlib.use('PDF')  # set directly after import matplotlib
# from matplotlib.backends.backend_pdf import PdfPages
# matplotlib.rc('ps', usedistiller='xpdf')  # ps2pdf
from matplotlib import pyplot as plt
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except OSError:
    plt.style.use('seaborn-darkgrid')

if __name__ == "__main__":

    acmaps = plt.colormaps()
    cmaps  = [ i for i in acmaps if not i.endswith('_r') ]
    cmaps.sort()

    # adapted from scipy cookbook
    a = np.outer(np.ones(10), np.arange(0, 1, 0.01))
    for i, m in enumerate(cmaps):
        print(m)
        # PDF
        # pdf_pages = PdfPages(m+".pdf")
        # w/o text
        fig = plt.figure(figsize=(0.3, 0.05))
        # w/ text
        # fig.subplots_adjust(top=1.0, bottom=0.0, left=0.0, right=0.5)
        fig.subplots_adjust(top=1.0, bottom=0.0, left=0.0, right=1.0)
        sub = plt.subplot(1, 1, 1)
        sub.axis("off")
        sub.imshow(a, aspect='auto', cmap=mpl.colormaps[m], origin="lower")
        # w/ text
        # plt.text(1.05, 0.1, m, transform=sub.transAxes, fontsize=8)
        # PNG
        fig.savefig(f"{m}.png", dpi=300, transparent=True, bbox_inches='tight',
                    pad_inches=0.0)
        # PDF
        # pdf_pages.savefig(fig)
        plt.close(fig)
        # PDF
        # pdf_pages.close()
