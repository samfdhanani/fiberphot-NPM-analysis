import numpy as np

def smooth_signal(x, window_len=10, window='flat'):
    """
    Smooth the data using a window with the requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) at both ends so that transient parts are minimized
    at the beginning and end of the output signal.

    Source: https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html

    Parameters:
        x: array_like, the input signal.
        window_len: int, the dimension of the smoothing window; should be an odd integer.
        window: str, the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'.
                'flat' window will produce a moving average smoothing.

    Returns:
        smoothed_signal: array_like, the smoothed signal.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s = np.r_[x[window_len-1:0:-1], x, x[-2:-window_len-1:-1]]

    if window == 'flat':  # Moving average
        w = np.ones(window_len, 'd')
    else:
        w = getattr(np, window)(window_len)

    y = np.convolve(w / w.sum(), s, mode='valid')

    return y[(int(window_len / 2) - 1):-int(window_len / 2)]
