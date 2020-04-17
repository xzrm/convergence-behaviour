class current_view_data:
    instances = []
    # singleton design pattern

    def __init__(self, frame=None):
        self.frame = frame
        self.ax = None
        # self.added_annot = set()
        self.added_annot = {}
        self.full_steps = None
        self.step_objects = None
        self.custom_lines_objs = {}
        self.phases = []
        self.curr_phase_number = None
        self.file_path = None

        self.__class__.instances.append(self)

    @property
    def current_phase(self):
        if self.curr_phase_number:
            return "Phase " + str(self.curr_phase_number)

    @classmethod
    def get_instance_by_frame(cls, frame):
        for instance in cls.instances:
            if instance.frame == frame:
                return instance

    @classmethod
    def delete_view(cls, frame):
        instance = cls.get_instance_by_frame(frame)
        print(cls.instances)
        if instance:
            cls.instances.remove(instance)
        print(cls.instances)
