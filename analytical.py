import numpy as np
from scipy.stats import norm


def _d1_d2(S, K, t, sigma, r):
    d1 = (
        np.log(S / K) +
        (r + 0.5 * sigma**2) * t
    ) / (sigma * np.sqrt(t))

    d2 = d1 - sigma * np.sqrt(t)

    return d1, d2


def Vanilla(S, K, t, sigma, r, option="call"):

    d1, d2 = _d1_d2(S, K, t, sigma, r)

    if option.lower() == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * t) * norm.cdf(d2)

    elif option.lower() == "put":
        return K * np.exp(-r * t) * norm.cdf(-d2) - S * norm.cdf(-d1)

    raise ValueError("option must be 'call' or 'put'")


def Digital(S, K, t, sigma, r, option="call"):

    _, d2 = _d1_d2(S, K, t, sigma, r)

    if option.lower() == "call":
        return np.exp(-r * t) * norm.cdf(d2)

    elif option.lower() == "put":
        return np.exp(-r * t) * norm.cdf(-d2)

    raise ValueError("option must be 'call' or 'put'")

