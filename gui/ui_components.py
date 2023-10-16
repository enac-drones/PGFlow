from __future__ import annotations
from gui.gui_sim import InteractivePlot
import matplotlib.pyplot as plt


class UIComponents:
    def __init__(self, interactive_plot: InteractivePlot):
        self.interactive_plot = interactive_plot
        self.ax_build = plt.axes(
            [0.01, 0.01, 0.1, 0.05]
        )  # Position of 'Build Mode' button
        self.ax_drone = plt.axes(
            [0.12, 0.01, 0.1, 0.05]
        )  # Position of 'Drone Mode' button
        self.ax_reset = plt.axes([0.23, 0.01, 0.1, 0.05])  # Position of 'Reset' button

        self.btn_build = plt.Button(self.ax_build, "Build Mode")
        self.btn_drone = plt.Button(self.ax_drone, "Drone Mode")
        self.btn_reset = plt.Button(self.ax_reset, "Reset")

        self.btn_build.on_clicked(self.on_build_mode)
        self.btn_drone.on_clicked(self.on_drone_mode)
        self.btn_reset.on_clicked(self.on_reset)

    def on_build_mode(self, event):
        # Switch to building mode
        self.interactive_plot.switch_to_build_mode()

    def on_drone_mode(self, event):
        # Switch to drone mode
        self.interactive_plot.switch_to_drone_mode()

    def on_reset(self, event):
        # Reset the interactive plot
        self.interactive_plot.reset()
