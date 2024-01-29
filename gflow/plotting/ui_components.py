from __future__ import annotations
# from gui.gui_sim import InteractivePlot
import matplotlib.pyplot as plt
from gflow.plotting.observer_utils import Observable



class UIComponents(Observable):
    def __init__(self, ax: plt.Axes):
        super().__init__()
        self.ax = ax
        self.fig = ax.figure
        self.buttons:dict[str, dict[str, plt.Axes|str|function]] = {
            'switch': {
                'axis': self.fig.add_axes([0.01, 0.01, 0.20, 0.05]),
                'label': "Run",
                'callback': self.on_run
            },
            'run': {
                'axis': self.fig.add_axes([0.22, 0.01, 0.1, 0.05]),
                'label': "Pause",
                'callback': self.on_pause
            },
            'reset': {
                'axis': self.fig.add_axes([0.33, 0.01, 0.1, 0.05]),
                'label': "Reset",
                'callback': self.on_reset
            },
            'case_generate': {
                'axis': self.fig.add_axes([0.6, 0.01, 0.15, 0.05]),
                'label': "Generate Case",
                'callback': self.on_generate
            }
        }
        
        # Initialize buttons and register callbacks
        for key, btn_info in self.buttons.items():
            button = plt.Button(btn_info['axis'], btn_info['label'])
            button.on_clicked(btn_info['callback'])
            self.buttons[key]['button'] = button

    def rename_button(self, button_key: str, new_label: str) -> None:
        if button_key in self.buttons:
            self.buttons[button_key]['button'].label.set_text(new_label)
        else:
            raise ValueError(f"No button found with the key '{button_key}'")
        
    def on_run(self, event):
        self.notify_observers("run")

    def on_pause(self, event):
        self.notify_observers("pause")

    def on_reset(self, event):
        self.notify_observers("reset")

    def on_generate(self, event):
        self.notify_observers("generate_case")

    # ... existing methods ...


 
