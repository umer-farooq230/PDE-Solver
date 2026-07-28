import numpy as np
import streamlit as st

from options import VanillaOption, DigitalOption, AmericanOption, BarrierOption
from pde_solver import PDESolver
from analytical import Vanilla, Digital
from visualization import PDEVisualizer

st.set_page_config(page_title="PDE Option Pricer", layout="wide")

FORMULAS = {
    "Vanilla": (
        r"\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 "
        r"\frac{\partial^2 V}{\partial S^2} + rS\frac{\partial V}{\partial S} - rV = 0",
        "Standard Black-Scholes PDE. Payoff at maturity is max(S-K,0) for a call "
        "or max(K-S,0) for a put. European exercise only.",
    ),
    "Digital": (
        r"\text{Payoff} = \mathbb{1}_{S>K} \ \text{(call)} \ \text{or} \ \mathbb{1}_{S<K} \ \text{(put)}",
        "Same Black-Scholes PDE, but the payoff is a discontinuous cash-or-nothing "
        "indicator instead of a smooth kink.",
    ),
    "American": (
        r"V(S,t) \geq \text{Payoff}(S), \quad \frac{\partial V}{\partial t} + "
        r"\frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2} + rS\frac{\partial V}{\partial S} - rV \leq 0",
        "Free-boundary problem: at every time step the PDE solution is floored "
        "against the immediate exercise payoff (early exercise allowed).",
    ),
    "Barrier": (
        r"V(S,t) = 0 \ \text{once} \ S \ \text{crosses the barrier } B",
        "Same PDE as vanilla, with the value knocked out to zero once the "
        "underlying crosses the barrier level (up-and-out or down-and-out).",
    ),
}

st.title("PDE Option Pricer")

with st.sidebar:
    st.header("1. Option")
    method = st.selectbox("Method", ["Vanilla", "Digital", "American", "Barrier"])
    option_type = st.selectbox("Type", ["call", "put"])

    st.header("2. Parameters")
    S0 = st.number_input("Spot (S0)", value=100.0, min_value=0.01)
    K = st.number_input("Strike (K)", value=100.0, min_value=0.01)
    T = st.number_input("Maturity T (yrs)", value=1.0, min_value=0.01)
    sigma = st.number_input("Volatility (sigma)", value=0.20, min_value=0.001, format="%.3f")
    r = st.number_input("Risk-free rate (r)", value=0.05, format="%.3f")

    barrier_type, barrier_level = None, None
    if method == "Barrier":
        barrier_type = st.selectbox("Barrier type", ["up_out", "down_out"])
        barrier_level = st.number_input("Barrier level", value=150.0, min_value=0.01)

    st.header("3. Grid")
    Smax = st.number_input("Smax", value=max(300.0, 3 * K), min_value=K + 1)
    M = st.slider("Space steps (M)", 50, 500, 200)
    N = st.slider("Time steps (N)", 100, 2000, 1000)

    st.header("4. Solver")
    solver_choice = st.selectbox("Method", ["Crank-Nicolson", "Implicit", "Explicit"])
    if solver_choice == "Explicit":
        st.caption("⚠ Explicit is conditionally stable — may blow up on coarse grids.")

    run = st.button("Solve", type="primary", use_container_width=True)

if "result" not in st.session_state:
    st.session_state.result = None

if run:
    if method == "Vanilla":
        option = VanillaOption(K=K, T=T, option_type=option_type)
    elif method == "Digital":
        option = DigitalOption(K=K, T=T, option_type=option_type)
    elif method == "American":
        option = AmericanOption(K=K, T=T, option_type=option_type)
    else:
        option = BarrierOption(K=K, T=T, option_type=option_type,
                                barrier_type=barrier_type, barrier_level=barrier_level)

    solver = PDESolver()
    solver_fn = {
        "Explicit": solver.explicit,
        "Implicit": solver.implicit,
        "Crank-Nicolson": solver.crank_nicolson,
    }[solver_choice]

    S, t, V = solver_fn(option, Smax=Smax, M=int(M), N=int(N), sigma=sigma, r=r)
    idx = int(np.abs(S - S0).argmin())
    pde_price = V[idx, 0]

    analytical_price = None
    if method == "Vanilla":
        analytical_price = Vanilla(S0, K, T, sigma, r, option_type)
    elif method == "Digital":
        analytical_price = Digital(S0, K, T, sigma, r, option_type)

    comparison = {}
    for name, fn in {"Explicit": solver.explicit, "Implicit": solver.implicit,
                      "Crank-Nicolson": solver.crank_nicolson}.items():
        try:
            _, _, Vc = fn(option, Smax=Smax, M=int(M), N=int(N), sigma=sigma, r=r)
            val = Vc[idx, 0]
            comparison[name] = val if np.isfinite(val) and abs(val) < 1e6 else np.nan
        except Exception:
            comparison[name] = np.nan

    st.session_state.result = dict(
        S=S, t=t, V=V, idx=idx, pde_price=pde_price,
        analytical_price=analytical_price, comparison=comparison,
        method=method, solver_choice=solver_choice, S0=S0,
    )

res = st.session_state.result

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader(f"{method if not res else res['method']} option — formula")
    latex, explanation = FORMULAS[method if not res else res["method"]]
    st.latex(latex)
    st.write(explanation)

    st.subheader("Results")
    if res:
        st.metric(f"PDE price ({res['solver_choice']})", f"{res['pde_price']:.4f}")
        if res["analytical_price"] is not None:
            diff = res["pde_price"] - res["analytical_price"]
            st.metric("Analytical (closed-form)", f"{res['analytical_price']:.4f}",
                       delta=f"{diff:+.4f} vs PDE")
        else:
            st.caption("No closed-form benchmark for this option type.")
    else:
        st.info("Set parameters and click **Solve**.")

with col_right:
    viz = PDEVisualizer()
    if res:
        st.subheader("Option Value Surface")
        st.plotly_chart(viz.surface(res["S"], res["t"], res["V"]), use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(viz.decay(res["t"], res["V"], res["idx"]), use_container_width=True)
        with c2:
            clean = {k: v for k, v in res["comparison"].items() if np.isfinite(v)}
            st.plotly_chart(viz.comparison(clean), use_container_width=True)
    else:
        st.info("Results will appear here after solving.")