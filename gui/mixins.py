import numpy as np

class SelectableMixin:
    def select(self):
        print("in selectable mixin select")
        # Logic to highlight or change the appearance when selected
        self.set_facecolor("red")

    def deselect(self):
        print("in selectable mixin deselect")
        # Logic to revert to the original appearance when deselected
        self.set_facecolor(self.original_color)


class ClickableMixin:
    def is_near(self, point, threshold=0.2):
        return np.linalg.norm(np.array(point) - self.position) < threshold
    