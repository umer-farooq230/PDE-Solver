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

## Project files

| File | What it does |
|---|---|
| `app.py` | The Streamlit dashboard. Collects your inputs in the sidebar, calls the solver, and displays the formula, results, and charts. |
| `options.py` | Defines each option type (Vanilla, Digital, American, Barrier) as a class: its payoff at maturity and its boundary conditions (value at S=0 and S=Smax). |
| `pde_solver.py` | The numerical engine. Builds the grid and steps the option value backward from maturity to today using the Explicit, Implicit, or Crank-Nicolson method. |
| `analytical.py` | Closed-form Black-Scholes formulas for Vanilla and Digital options, used to sanity-check the PDE results. |
| `visualization.py` | Builds the three Plotly charts: the 3D value surface, the time-decay line chart, and the solver comparison bar chart. |
| `test.py` | A quick script that runs the analytical formulas and the PDE solver once and prints the results, to confirm everything imports and runs correctly. |

## The math behind it

An option's value V, as a function of stock price S and time t, follows the **Black-Scholes partial differential equation**:

```
∂V/∂t + ½σ²S² ∂²V/∂S² + rS ∂V/∂S − rV = 0
```

In words: how the option's value changes over time is determined by how curved the payoff is with respect to the stock price (the σ² term — this is where volatility comes in), how sensitive it is to the stock price directly (the r term), and discounting (the −rV term).

Instead of solving this equation with algebra (only possible for simple payoffs like Vanilla and Digital), we solve it numerically:

1. **Discretize** — replace the continuous S and t with a grid of discrete points, spaced `dS` apart in price and `dt` apart in time.
2. **Set the known values** — at maturity, V is just the payoff. At the top and bottom of the grid, V is set by the boundary conditions.
3. **Step backward** — starting from maturity, compute V one time step earlier using the values one step later, replacing the derivatives in the PDE with finite differences (approximating a slope with `(V[i+1] - V[i-1]) / (2·dS)`, and curvature with a similar formula using three neighboring points).
4. **Repeat** until reaching today (t=0), at which point V at every stock price is known — this is the full surface. The price at your chosen spot S0 is just one point read off that surface.

The three solvers (Explicit, Implicit, Crank-Nicolson) differ only in *which* time step's values are used to approximate the derivatives — that's what makes them behave differently in terms of speed, stability, and accuracy.

For American options, an extra check is added at every time step: after computing V, it's floored against the immediate exercise payoff, since the holder could choose to exercise early. For Barrier options, V is set to zero wherever the stock price has crossed the barrier.

## Installation

Requires Python 3.9+.

```bash
pip install streamlit numpy scipy plotly
```

## Usage

1. Make sure `app.py`, `options.py`, `pde_solver.py`, `analytical.py`, and `visualization.py` are all in the same folder.
2. From that folder, run:

```bash
streamlit run app.py
```

3. Your browser will open the dashboard. In the sidebar:
   - Pick an option method (Vanilla, Digital, American, Barrier) and call/put type.
   - Enter the option parameters (spot, strike, maturity, volatility, rate).
   - For Barrier options, set the barrier type and level.
   - Set the grid size (Smax, M, N) — larger values are more accurate but slower.
   - Pick a solver (Crank-Nicolson is the recommended default).
4. Click **Solve**. The formula, price, 3D surface, time-decay chart, and solver comparison will appear below.

You can also try it without installing anything, at the deployed link above.

## Visuals

- **Option Value Surface** — a 3D plot showing the option's value across every stock price and every point in time. This is the main output: it shows not just today's price, but how the option would be valued at any spot price at any time before expiry.
- **Time Decay** — a 2D line chart showing how the option's value changes over time at the spot price you set, illustrating how the option loses (or gains) value as expiry approaches.
- **Solver Comparison** — a bar chart comparing the price you get from Explicit, Implicit, and Crank-Nicolson side by side, so you can see how closely the three methods agree (or where Explicit becomes unstable).
