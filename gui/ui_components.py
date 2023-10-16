from __future__ import annotations
# from gui.gui_sim import InteractivePlot
import matplotlib.pyplot as plt
from gui.observer_utils import Observable, Observer



class UIComponents(Observable):
    def __init__(self, ax: plt.Axes):
        super().__init__()
        self.ax = ax
        self.fig = ax.figure
        self.ax_build = self.fig.add_axes(
            [0.01, 0.01, 0.15, 0.05]
        )  # Position of 'Build Mode' button
        # self.ax_drone = self.fig.add_axes(
        #     [0.12, 0.01, 0.1, 0.05]
        # )  # Position of 'Drone Mode' button
        self.ax_reset = self.fig.add_axes([0.23, 0.01, 0.1, 0.05])  # Position of 'Reset' button

        self.btn_build = plt.Button(self.ax_build, "Switch Mode")
        # self.btn_drone = plt.Button(self.ax_drone, "Drone Mode")
        self.btn_reset = plt.Button(self.ax_reset, "Reset")

        self.btn_build.on_clicked(self.on_build_mode)
        # self.btn_drone.on_clicked(self.on_drone_mode)
        self.btn_reset.on_clicked(self.on_reset)

    def on_build_mode(self, event):
        # Switch to building mode
        # pass
        self.notify_observers("build_mode")

    def on_reset(self, event):
        self.notify_observers("reset")

