class step_annotation:
    def __init__(self, ax, step, x, y):
        self.ax = ax
        self.c = ax.get_figure().canvas
        self.x = x
        self.y = y

        self.step = step

        print(self.x, self.y)

        self.annot = self.ax.annotate(
            "",
            xy=(self.x, self.y),
            xytext=(-20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
        )

        text = "Step no: {}\nLoadcase: {}".format(
            str(self.step.get_step_no()),
            str(self.step.get_loadcase()),
            str(self.step.total_iterations),
        )

        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.7)
        self.annot.draggable()


class updatable_annotation:
    instances = []

    def __init__(self, ax, data_xy):

        self.ax = ax
        self.canvas = self.ax.get_figure().canvas
        self.data_xy = data_xy

        self.annot = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(-20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
        )

        self.annot.set_visible(False)

        self.__class__.instances.append(self)

    def update_annot(self, ind, curr_data):
        x, y = self.data_xy.get_data()

        step_idx = ind["ind"][0]
        self.annot.xy = (x[step_idx], y[step_idx])

        text = "Step no: {}\nLoadcase: {}\nTotal iterations: {} \nVariation: {}".format(
            str(curr_data.step_objects[step_idx].get_step_no()),
            str(curr_data.step_objects[step_idx].get_loadcase()),
            str(x[step_idx]),
            str(y[step_idx]),
        )

        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.7)

    def hover(self, event, curr_data):

        visiblity = self.annot.get_visible()
        if event.inaxes == self.ax:
            contains, idx = self.data_xy.contains(
                event
            )  # check if cursor hovers over one of full_steps array and returns index
            # Result form example: True/False {'ind': array([53], dtype=int32)}
            if contains:
                self.update_annot(idx, curr_data)
                self.annot.set_visible(True)
                self.canvas.draw_idle()
            else:
                if visiblity:
                    self.annot.set_visible(False)
                    self.canvas.draw_idle()

    @classmethod
    def get_instance_by_axes(cls, ax):
        for instance in cls.instances:
            if instance.ax == ax:
                return instance
