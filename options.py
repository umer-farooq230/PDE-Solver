import numpy as np


class Option:
    def __init__(self, K, T, option_type="call", barrier_type=None, barrier_level=None):
        self.K = K
        self.T = T
        self.option_type = option_type.lower()
        self.barrier_type = barrier_type
        self.barrier_level = barrier_level

        # Used by the PDE solver
        self.early_exercise = False

    # Payoff (override)
    def payoff(self, S):
        raise NotImplementedError

    # Left Boundary S = 0
    def boundary_left(self, t, r):
        raise NotImplementedError

    # Right Boundary S = Smax
    def boundary_right(self, Smax, t, r):
        raise NotImplementedError


class VanillaOption(Option):

    def payoff(self, S):
        if self.option_type == "call":
            return np.maximum(S - self.K, 0)

        return np.maximum(self.K - S, 0)

    def boundary_left(self, t, r):
        tau = self.T - t

        if self.option_type == "call":
            return 0.0

        return self.K * np.exp(-r * tau)

    def boundary_right(self, Smax, t, r):
        tau = self.T - t

        if self.option_type == "call":
            return Smax - self.K * np.exp(-r * tau)

        return 0.0



class DigitalOption(Option):

    def payoff(self, S):
        if self.option_type == "call":
            return np.where(S > self.K, 1.0, 0.0)

        return np.where(S < self.K, 1.0, 0.0)

    def boundary_left(self, t, r):
        tau = self.T - t

        if self.option_type == "call":
            return 0.0

        return np.exp(-r * tau)

    def boundary_right(self, Smax, t, r):
        tau = self.T - t

        if self.option_type == "call":
            return np.exp(-r * tau)

        return 0.0


class AmericanOption(Option):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.early_exercise = True

    def payoff(self, S):
        if self.option_type == "call":
            return np.maximum(S - self.K, 0)

        return np.maximum(self.K - S, 0)

    def boundary_left(self, t, r):

        if self.option_type == "call":
            return 0.0

        return self.K

    def boundary_right(self, Smax, t, r):

        if self.option_type == "call":
            return Smax - self.K

        return 0.0


class BarrierOption(Option):

    def payoff(self, S):

        if self.option_type == "call":
            return np.maximum(S - self.K, 0)

        return np.maximum(self.K - S, 0)

    def boundary_left(self, t, r):

        tau = self.T - t

        if self.barrier_type == "down_out":
            return 0.0

        if self.option_type == "call":
            return 0.0

        return self.K * np.exp(-r * tau)

    def boundary_right(self, Smax, t, r):

        tau = self.T - t

        if self.barrier_type == "up_out":
            return 0.0

        if self.option_type == "call":
            return Smax - self.K * np.exp(-r * tau)

        return 0.0
    
    def apply_barrier(self, V, S):

        if self.barrier_type == "up_out":
            V[S >= self.barrier_level] = 0
    
        elif self.barrier_type == "down_out":
            V[S <= self.barrier_level] = 0
    
        return V