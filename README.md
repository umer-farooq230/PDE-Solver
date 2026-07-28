# PDE Solver - Option Pricer

A small dashboard that prices options by solving the Black-Scholes equation on a grid, instead of using the closed-form formula. It lets you see how the price is built up across every stock price and every point in time, not just at today's spot price.

**Live app:** https://pde-solver.streamlit.app/

## What this project does

Given an option (strike, maturity, volatility, interest rate), the app:

1. Builds a grid of stock prices (from 0 up to some max value) and time steps (from today to maturity).
2. Starts at maturity, where the option's value is just its payoff.
3. Works backward in time, step by step, updating the value at every stock price using a numerical scheme (see below).
4. Ends up with the option's value today, at every possible stock price — which is what the 3D surface shows.

For simple option types, this is checked against the exact textbook formula (Black-Scholes) to confirm the numbers line up.

## Option types

- **Vanilla** — the standard call/put. Pays off `max(S - K, 0)` for a call or `max(K - S, 0)` for a put at maturity. Can only be exercised at maturity (European style).
- **Digital** — pays a fixed amount (1) if the stock ends up above (or below) the strike, and nothing otherwise. Same PDE as Vanilla, but a sharper, all-or-nothing payoff.
- **American** — like Vanilla, but can be exercised at *any* time before maturity, not just at the end. The solver checks at every time step whether exercising early is worth more than holding, and takes the higher value.
- **Barrier** — like Vanilla, but the option is knocked out (becomes worthless) if the stock price crosses a barrier level, either from below (up-and-out) or above (down-and-out).

## Parameters you set

| Parameter | Meaning |
|---|---|
| Spot (S0) | Current stock price |
| Strike (K) | Price at which the option can be exercised |
| Maturity (T) | Time until expiry, in years |
| Volatility (sigma) | How much the stock price fluctuates |
| Risk-free rate (r) | Interest rate used for discounting |
| Barrier level | Knockout price, only for Barrier options |
| Smax | Highest stock price on the grid (should be well above the strike) |
| M | Number of stock-price steps in the grid (finer = more accurate, slower) |
| N | Number of time steps (finer = more accurate, slower) |

## Solvers

Three different numerical methods are offered for stepping the grid backward in time. They all solve the same equation, but trade off speed, stability, and accuracy differently:

- **Explicit** — the simplest method: each new value is computed directly from the previous time step's neighbors. Fast per step, but only stable if the time steps are small enough relative to the grid spacing — with a coarse grid it can blow up to unrealistic numbers.
- **Implicit** — solves a small system of equations at each time step instead of computing directly. Slightly more work per step, but stable no matter how coarse the grid is.
- **Crank-Nicolson** — a blend of Explicit and Implicit. Generally the most accurate of the three for a given grid size, and is stable. This is the recommended default.

## Visuals

- **Option Value Surface** — a 3D plot showing the option's value across every stock price and every point in time. This is the main output: it shows not just today's price, but how the option would be valued at any spot price at any time before expiry.
- **Time Decay** — a 2D line chart showing how the option's value changes over time at the spot price you set, illustrating how the option loses (or gains) value as expiry approaches.
- **Solver Comparison** — a bar chart comparing the price you get from Explicit, Implicit, and Crank-Nicolson side by side, so you can see how closely the three methods agree (or where Explicit becomes unstable).
