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
        self.ax_run = self.fig.add_axes(
            [0.17, 0.01, 0.1, 0.05]
        )  # Position of 'Drone Mode' button
        self.ax_reset = self.fig.add_axes([0.28, 0.01, 0.1, 0.05])  # Position of 'Reset' button

        self.btn_build = plt.Button(self.ax_build, "Switch Mode")
        self.btn_run = plt.Button(self.ax_run, "Run")
        self.btn_reset = plt.Button(self.ax_reset, "Reset")

        self.btn_build.on_clicked(self.on_build_mode)
        self.btn_run.on_clicked(self.on_run)
        self.btn_reset.on_clicked(self.on_reset)

    def on_build_mode(self, event):
        # Switch to building mode
        # pass
        self.notify_observers("build_mode")

    def on_reset(self, event):
        self.notify_observers("reset")

    def on_run(self,event):
        self.notify_observers("run")

