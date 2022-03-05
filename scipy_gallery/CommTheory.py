#!/usr/bin/env python
# coding: utf-8

# Communication theory
# ======================================================================
#
# These two examples illustrate simple simulation of a digital BPSK
# modulated communication system where only one sample per symbol is used,
# and np.signal is affected only by AWGN noise.
#
# In the first example, we cycle through different np.signal to noise values,
# and the np.signal length is a function of theoretical probability of error.
# As a rule of thumb, we want to count about 100 errors for each SNR
# value, which determines the length of the np.signal (and noise) vector(s).


#!/usr/bin/python
# BPSK digital modulation example
# by Ivo Maljevic

import numpy as np
from scipy.special import erfc
import matplotlib.pyplot as plt
from scipy.special import erfc

SNR_MIN = 0
SNR_MAX = 9
Eb_No_dB = np.arange(SNR_MIN, SNR_MAX + 1)
SNR = 10**(Eb_No_dB / 10.0)  # linear SNR

Pe = np.empty(np.shape(SNR))
BER = np.empty(np.shape(SNR))

loop = 0
for snr in SNR:      # SNR loop
    Pe[loop] = 0.5 * erfc(np.sqrt(snr))
    # vector length is a function of Pe
    VEC_SIZE = int(np.ceil(100 / Pe[loop]))

    # np.signal vector, new vector for each SNR value
    s = 2 * np.random.randint(0, high=2, size=VEC_SIZE) - 1

    # linear power of the noise; average np.signal power = 1
    No = 1.0 / snr

    # noise
    n = np.sqrt(No / 2) * np.random.randn(VEC_SIZE)

    # np.signal + noise
    x = s + n

    # decode received np.signal + noise
    y = np.sign(x)

    # find erroneous symbols
    err = np.where(y != s)
    error_sum = float(len(err[0]))
    BER[loop] = error_sum / VEC_SIZE
    print('Eb_No_dB=%4.2f, BER=%10.4e, Pe=%10.4e' %
          (Eb_No_dB[loop], BER[loop], Pe[loop]))
    loop += 1

plt.figure()
#plt.semilogy(Eb_No_dB, Pe,'r',Eb_No_dB, BER,'s')
plt.semilogy(Eb_No_dB, Pe, 'r', linewidth=2)
plt.semilogy(Eb_No_dB, BER, '-s')
plt.grid(True)
plt.legend(('analytical', 'simulation'))
plt.xlabel('Eb/No (dB)')
plt.ylabel('BER')


# In the second, slightly modified example, the problem of np.signal length
# growth is solved by braking a np.signal into frames.Namely, the number of
# samples for a given SNR grows quickly, so that the simulation above is
# not practical for Eb/No values greater than 9 or 10 dB.


# BPSK digital modulation: modified example
# by Ivo Maljevic


rand = np.random.rand
normal = np.random.normal

SNR_MIN = 0
SNR_MAX = 10
FrameSize = 10000
Eb_No_dB = np.arange(SNR_MIN, SNR_MAX + 1)
Eb_No_lin = 10**(Eb_No_dB / 10.0)  # linear SNR

# Allocate memory
Pe = np.empty(np.shape(Eb_No_lin))
BER = np.empty(np.shape(Eb_No_lin))

# np.signal vector (for faster exec we can repeat the same frame)
s = 2 * np.random.randint(0, high=2, size=FrameSize) - 1

loop = 0
for snr in Eb_No_lin:
    No = 1.0 / snr
    Pe[loop] = 0.5 * erfc(np.sqrt(snr))
    nFrames = np.ceil(100.0 / FrameSize / Pe[loop])
    error_sum = 0
    scale = np.sqrt(No / 2)

    for frame in np.arange(nFrames):
        # noise
        n = normal(scale=scale, size=FrameSize)

        # received np.signal + noise
        x = s + n

        # detection (information is encoded in np.signal phase)
        y = np.sign(x)

        # error counting
        err = np.where(y != s)
        error_sum += len(err[0])

        # end of frame loop
        ##################################################

    BER[loop] = error_sum / (FrameSize * nFrames)  # SNR loop level
    print('Eb_No_dB=%2d, BER=%10.4e, Pe[loop]=%10.4e' % (
        Eb_No_dB[loop], BER[loop], Pe[loop]))
    loop += 1

plt.figure()
plt.semilogy(Eb_No_dB, Pe, 'r', linewidth=2)
plt.semilogy(Eb_No_dB, BER, '-s')
plt.grid(True)
plt.legend(('analytical', 'simulation'))
plt.xlabel('Eb/No (dB)')
plt.ylabel('BER')
plt.show()
