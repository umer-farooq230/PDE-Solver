import plotly.graph_objects as go
import plotly.express as px
import numpy as np


class PDEVisualizer:

    def surface(self, S, t, V):
        """
        Large 3D surface
        """
        fig = go.Figure(
            data=[
                go.Surface(
                    x=S,
                    y=t,
                    z=V.T
                )
            ]
        )

        fig.update_layout(
            title="Option Value Surface",
            scene=dict(
                xaxis_title="Stock Price",
                yaxis_title="Time",
                zaxis_title="Option Value"
            ),
            height=650
        )

        return fig


    def decay(self, t, V, stock_index):
        """
        Small time decay chart
        """
        fig = px.line(
            x=t,
            y=V[stock_index, :],
            labels={
                "x": "Time",
                "y": "Option Value"
            },
            title="Time Decay"
        )

        fig.update_layout(height=250)

        return fig


    def comparison(self, prices):
        """
        Small bar chart
        prices = {
            "Explicit": 10.41,
            "Implicit": 10.46,
            "Crank-Nicolson": 10.45
        }
        """

        fig = px.bar(
            x=list(prices.keys()),
            y=list(prices.values()),
            title="Solver Comparison"
        )

        fig.update_layout(height=250)

        return fig