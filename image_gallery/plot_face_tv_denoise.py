"""
Total Variation denoising
===========================

This example demoes Total-Variation (TV) denoising on a Racoon face.
"""

import numpy as np
import scipy
import scipy.misc
import matplotlib.pyplot as plt
try:
    from skimage.restoration import denoise_tv_chambolle
except ImportError:
    # skimage < 0.12
    from skimage.filters import denoise_tv_chambolle

f = scipy.misc.face(gray=True)
f = f[230:290, 220:320]

noisy = f + 0.4 * f.std() * np.random.random(f.shape)

tv_denoised = denoise_tv_chambolle(noisy, weight=10)


plt.figure(figsize=(12, 2.8))

plt.subplot(141)
plt.imshow(noisy, cmap=plt.cm.gray, vmin=40, vmax=220)
plt.axis('off')
plt.title('noisy', fontsize=20)

plt.subplot(142)
plt.imshow(tv_denoised, cmap=plt.cm.gray, vmin=40, vmax=220)
plt.axis('off')
plt.title('TV denoising', fontsize=20)

tv_denoised = denoise_tv_chambolle(noisy, weight=50)
plt.subplot(143)
plt.imshow(tv_denoised, cmap=plt.cm.gray, vmin=40, vmax=220)
plt.axis('off')
plt.title('(more) TV denoising', fontsize=20)

plt.subplot(144)
plt.imshow(f, cmap=plt.cm.gray, vmin=40, vmax=220)
plt.axis('off')

plt.subplots_adjust(wspace=0.02, hspace=0.02, top=0.9, bottom=0, left=0,
                    right=1)
plt.show()
