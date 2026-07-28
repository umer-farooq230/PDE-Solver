import numpy as np
from scipy.linalg import solve_banded


class PDESolver:

    def _grid(self, Smax, M, N, T):
        dS = Smax / M
        dt = T / N
        S = np.linspace(0, Smax, M + 1)
        t = np.linspace(0, T, N + 1)
        return S, t, dS, dt

    def _initialize(self, option, S, t, r):
        V = np.zeros((len(S), len(t)))
        V[:, -1] = option.payoff(S)

        for j in range(len(t)):
            V[0, j] = option.boundary_left(t[j], r)
            V[-1, j] = option.boundary_right(S[-1], t[j], r)

        return V

    def _apply_constraints(self, option, V, S, j):
        if option.early_exercise:
            V[:, j] = np.maximum(V[:, j], option.payoff(S))
        if hasattr(option, "apply_barrier"):
            V[:, j] = option.apply_barrier(V[:, j], S)
        return V

    def explicit(self, option, Smax, M, N, sigma, r):
        S, t, dS, dt = self._grid(Smax, M, N, option.T)
        V = self._initialize(option, S, t, r)

        i = np.arange(1, M)
        a = 0.5 * dt * (sigma**2 * i**2 - r * i)
        b = 1 - dt * (sigma**2 * i**2 + r)
        c = 0.5 * dt * (sigma**2 * i**2 + r * i)

        for j in range(N - 1, -1, -1):
            V[1:M, j] = a * V[0:M - 1, j + 1] + b * V[1:M, j + 1] + c * V[2:M + 1, j + 1]
            V[0, j] = option.boundary_left(t[j], r)
            V[-1, j] = option.boundary_right(S[-1], t[j], r)
            V = self._apply_constraints(option, V, S, j)

        return S, t, V

    def implicit(self, option, Smax, M, N, sigma, r):
        S, t, dS, dt = self._grid(Smax, M, N, option.T)
        V = self._initialize(option, S, t, r)

        i = np.arange(1, M)
        a = 0.5 * dt * (sigma**2 * i**2 - r * i)
        b = 1 + dt * (sigma**2 * i**2 + r)
        c = 0.5 * dt * (sigma**2 * i**2 + r * i)

        ab = np.zeros((3, M - 1))
        ab[0, 1:] = -c[:-1]
        ab[1, :] = b
        ab[2, :-1] = -a[1:]

        for j in range(N - 1, -1, -1):
            rhs = V[1:M, j + 1].copy()
            rhs[0] += a[0] * option.boundary_left(t[j], r)
            rhs[-1] += c[-1] * option.boundary_right(S[-1], t[j], r)

            V[1:M, j] = solve_banded((1, 1), ab, rhs)
            V[0, j] = option.boundary_left(t[j], r)
            V[-1, j] = option.boundary_right(S[-1], t[j], r)
            V = self._apply_constraints(option, V, S, j)

        return S, t, V

    def crank_nicolson(self, option, Smax, M, N, sigma, r):
        S, t, dS, dt = self._grid(Smax, M, N, option.T)
        V = self._initialize(option, S, t, r)

        i = np.arange(1, M)
        alpha = 0.25 * dt * (sigma**2 * i**2 - r * i)
        beta = 0.25 * dt * (sigma**2 * i**2 + r * i)
        gamma = 0.5 * dt * (sigma**2 * i**2 + r)

        ab = np.zeros((3, M - 1))
        ab[0, 1:] = -beta[:-1]
        ab[1, :] = 1 + gamma
        ab[2, :-1] = -alpha[1:]

        for j in range(N - 1, -1, -1):
            rhs = (
                alpha * V[0:M - 1, j + 1]
                + (1 - gamma) * V[1:M, j + 1]
                + beta * V[2:M + 1, j + 1]
            )
            rhs[0] += alpha[0] * option.boundary_left(t[j], r)
            rhs[-1] += beta[-1] * option.boundary_right(S[-1], t[j], r)

            V[1:M, j] = solve_banded((1, 1), ab, rhs)
            V[0, j] = option.boundary_left(t[j], r)
            V[-1, j] = option.boundary_right(S[-1], t[j], r)
            V = self._apply_constraints(option, V, S, j)

        return S, t, V