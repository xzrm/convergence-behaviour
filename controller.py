import tkinter as tk
import numpy as np
from functools import wraps
import os
import tab_data
from draggable_lines import draggable_line
from annotation import step_annotation, updatable_annotation
from view import View
import data
import phases


class Controller():
    def __init__(self):
        self.root = tk.Tk()

        self.view = View(self.root)
        self.view.sidepanel.plot_button.bind("<Button>", self.plot_convergence)
        self.view.sidepanel.clear_button.bind("<Button>", self.clear_plot)

        self.view.menubar.menu.entryconfig(self.view.menubar.menu.index("Read file"), command=self.read_outfile_path)
        self.view.menubar.menu.entryconfig(self.view.menubar.menu.index("New"), command=self.add_new_tab)
        self.view.menubar.menu.entryconfig(self.view.menubar.menu.index("Close"), command=self.delete_selected_tab)

        self.view.listbox_steps.add_button.bind("<Button>",
                                                lambda event,
                                                view_member=self.view.listbox_steps,
                                                tab_attr="added_annot":
                                                self.draw_object(view_member, tab_attr))

        self.view.listbox_steps.delete_selected_button.bind("<Button>",
                                                            lambda event,
                                                            view_member=self.view.listbox_steps,
                                                            tab_attr="added_annot":
                                                            self.delete_object(view_member, tab_attr))

        self.view.listbox_lines.add_button.bind("<Button>",
                                                lambda event,
                                                view_member=self.view.listbox_lines,
                                                tab_attr="custom_lines_objs":
                                                self.draw_object(view_member, tab_attr))

        self.view.listbox_lines.delete_selected_button.bind("<Button>",
                                                            lambda event,
                                                            view_member=self.view.listbox_lines,
                                                            tab_attr="custom_lines_objs":
                                                            self.delete_object(view_member, tab_attr))

        # self.tabs = {}  # dict in form of {'.!frame4.!notebook.!frame': <tab_data.Tab object at 0x0D7C27D0>, ...}
        self.add_new_tab()

    def read_outfile_path(self):
        self.outfile_path = self.view.menubar.read_file()
        self.file_name = os.path.basename(self.outfile_path)

        curr_tab = self.view.plotview.get_current_tab_obj()
        if(self.file_name):
            self.view.plotview.notebook.tab(curr_tab, text=self.file_name)

        self.curr_view_data.file_path = self.outfile_path
        # self.tabs[self.curr_tab].file_path = self.outfile_path
        # self.set_current_plotview()

        self.update_droplist_settings()
        self.ax.clear()
        self.canvas.draw()

    def add_new_tab(self):
        self.outfile_path = ''
        tab = self.view.plotview.add_tab()
        tab.bind("<Visibility>", self.on_visibility)
        tab_object = self.view.plotview.notebook.tabs()[-1]
        # tab_object -> .!frame3.!notebook.!frame + number

        # self.tabs[tab_object] = tab_data.current_view_data()
        # self.view.plotview.notebook.select(tab_object)

        self.curr_view_data = tab_data.current_view_data(tab_object)

        self.view.plotview.notebook.select(tab_object)

    # def set_current_plotview(self):
    #     self.curr_frame = self.view.plotview.get_current_tab_obj().split('.')[3]
    #     self.curr_tab = self.view.plotview.get_current_tab_obj()
    #     print("Current frame", self.curr_frame, "Current tab", self.curr_tab)

    #     self.curr_view_data = tab_data.current_view_data.get_instance_by_frame(self.curr_tab)

    #     self.ax = self.view.plotview.tabs_content[self.curr_frame]
    #     self.fig = self.ax.get_figure()
    #     self.canvas = self.fig.canvas

    def update_plotview(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.curr_frame = self.view.plotview.get_current_tab_obj().split('.')[3]
            self.curr_tab = self.view.plotview.get_current_tab_obj()
            print("Current frame", self.curr_frame, "Current tab", self.curr_tab)
            self.curr_view_data = tab_data.current_view_data.get_instance_by_frame(self.curr_tab)

            self.ax = self.view.plotview.tabs_content[self.curr_frame]
            self.fig = self.ax.get_figure()
            self.canvas = self.fig.canvas
            func(self, *args, **kwargs)

        return wrapper

    def delete_selected_tab(self):
        curr_tab = self.view.plotview.get_current_tab_obj()
        self.view.plotview.delete_selected_tab()
        tab_data.current_view_data.delete_view(self.curr_tab)
        if(len(tab_data.current_view_data.instances)) == 0:
            self.add_new_tab()
        # del self.tabs[curr_tab]

    def run(self):
        self.root.title("Convergence")
        self.root.deiconify()
        self.root.mainloop()

    def clear_plot(self, event):
        self.ax.clear()
        self.view.listbox_steps.delete_all()
        self.view.listbox_lines.delete_all()
        self.canvas.draw()

    def prepare_results(self):
        # self.outfile_path = self.tabs[self.curr_tab].file_path
        self.outfile_path = self.curr_view_data.file_path
        self.phase_number = int(self.view.sidepanel.phase_droplist.current() + 1)
        self.norm = self.view.sidepanel.norm_droplist.get() + "_norm"
        self.tolerance = float(self.view.sidepanel.tolerance_entry.get())
        try:

            self.text_list = phases.text_single_phase(self.outfile_path, self.phase_number)
            if self.text_list == None:
                self.text_list = phases.text_analaysis_no_phases(self.outfile_path)

        except (AttributeError, FileNotFoundError):
            print("Read .out file")
            return False

        self.step_objects, self.convergence = data.get_data(self.text_list, self.norm, self.tolerance)

        self.steps_unconv, self.variations_unconv = self.unpack(self.convergence.itera_unconv_pairs)
        self.steps_conv_other, self.variations_conv_other = self.unpack(self.convergence.converged_norm_other)
        self.steps_conv_this, self.variations_conv_this = self.unpack(self.convergence.converged_norm_this)
        self.steps_all, self.variation_all = self.unpack(self.convergence.full_step_itera)

        self.step_objects_array = np.array(self.step_objects)

        # self.tabs[self.curr_tab].step_objects = self.step_objects
        # self.tabs[self.curr_tab].curr_phase_number = self.phase_number

        self.curr_view_data.step_objects = self.step_objects
        self.curr_view_data.curr_phase_number = self.phase_number

        return True

    @update_plotview
    def plot_convergence(self, event):
        # self.set_current_plotview()
        if not self.prepare_results():
            return

        self.ax.clear()

        self.ax.plot((list(range(1, len(self.convergence.all_iterations) + 1))), self.convergence.all_iterations, color='blue', lw=0.5, label=self.view.sidepanel.norm_droplist.get().title() + " norm")

        self.ax.axhline(y=self.tolerance, lw=1.5, color='red', linestyle=':', label='Convergence tolerance')

        for step in self.convergence.full_step_itera:
            self.ax.axvline(x=step[0], color='g', lw=0.5, linestyle='-')
        self.full_steps, = self.ax.plot(self.steps_all, self.variation_all, 'gD', markersize=4)

        self.curr_view_data.full_steps = self.full_steps
        self.ax.plot(self.steps_unconv, self.variations_unconv, 'rD', markersize=4, label='Unconverged steps')
        self.ax.plot(self.steps_conv_this, self.variations_conv_this, 'gD', markersize=4, label='Converged steps')
        self.ax.plot(self.steps_conv_other, self.variations_conv_other, 'yD', markersize=4, label='Converged steps - other norm')

        self.plot_setting()
        self.canvas.draw()
        self.canvas.mpl_connect("motion_notify_event", lambda event, arg=self.curr_view_data: self.updatable_annot.hover(event, arg))


        self.draw_object(self.view.listbox_steps, "added_annot")
        self.draw_object(self.view.listbox_lines, "custom_lines_objs")

    def plot_setting(self):
        self.ax.set_yscale('log')
        self.ax.set_ylabel('log(variation)')
        self.ax.set_xlabel('total iterations')
        self.ax.grid(True, which="both", color='0.65', ls="--")
        self.ax.legend(loc="upper left", prop={'size': 8}, framealpha=0.7)

        self.updatable_annot = updatable_annotation(self.ax, self.full_steps)

    def unpack(self, iterable):
        if(iterable):
            unpacked_elements_1, unpacked_elements_2 = list(zip(*iterable))
            return unpacked_elements_1, unpacked_elements_2
        return [], []

    def update_droplist_settings(self):
        print(self.outfile_path)
        try:
            analysis_phases = phases.get_phases(self.outfile_path)
            print(type(analysis_phases))
            # self.tabs[self.curr_tab].phases = analysis_phases
            self.curr_view_data.phases = analysis_phases
            self.view.sidepanel.set_droplist_values(analysis_phases)
        except (AttributeError, FileNotFoundError):
            self.view.sidepanel.set_droplist_values([])

        if self.view.sidepanel.get_droplist_values():
            self.view.sidepanel.phase_droplist.current(0)

    def find_loadstep(self, tab_object, step_num):
        if step_num is None:
            return None
        if tab_object.step_objects is None:
            return None
        for step_obj in tab_object.step_objects:
            if step_obj.step_no == int(step_num):
                return step_obj

    def add_widget_entry_value(self, view_member):
        value = view_member.add_value()
        return value

    def draw_object(self, view_member, attr):
        print("Annot: ", attr)

        tab = self.curr_view_data

        tab_attr = getattr(tab, attr)
        value = self.add_widget_entry_value(view_member)

        for val in view_member.listbox.get(0, tk.END):
            print("value", val)

            if val not in tab_attr.keys():
                print("not in keys")
                if attr == "added_annot":

                    step_obj = self.find_loadstep(tab, value)
                    if not step_obj:
                        view_member.clear_text()
                        view_member.delete_by_value(value)
                        return

                    x = int(getattr(step_obj, "total_iterations"))
                    y = float(getattr(step_obj, self.norm)[-1])
                    new_annot = step_annotation(self.ax, step_obj, x, y)
                    tab_attr[val] = new_annot.annot

                elif attr == "custom_lines_objs":
                    new_line = draggable_line(self.ax, "v", val)
                    new_line.updater.add_callback(self.update_listbox_entry)
                    tab_attr[val] = new_line
            else:
                if tab_attr[val] not in self.ax.get_children():
                    print("not in children")
                    if attr == "added_annot":
                        step_obj = self.find_loadstep(tab, val)
                        x = int(getattr(step_obj, "total_iterations"))
                        y = float(getattr(step_obj, self.norm)[-1])
                        new_annot = step_annotation(self.ax, step_obj, x, y)
                        tab_attr[val] = new_annot.annot
                    elif attr == "custom_lines_objs":
                        self.ax.lines.append(tab_attr[val].line)

        self.canvas.draw()
        view_member.clear_text()

    def delete_object(self, view_member, tab_attr):
        deleted = view_member.delete_selected()
        # tab = self.tabs[self.curr_tab]

        tab = self.curr_view_data
        attr = getattr(tab, tab_attr)
        for val in deleted:
            obj = attr[int(val)]
            if tab_attr == "added_annot":
                self.ax.texts.remove(obj)
            elif tab_attr == "custom_lines_objs":
                self.ax.lines.remove(obj.line)
            else:
                raise ValueError(tab_attr)

            del attr[int(val)]
        self.canvas.draw()  # AS DECORATOR!

    @update_plotview
    def on_visibility(self, event):
        self.full_steps = self.curr_view_data.full_steps

        self.view.listbox_steps.delete_all()
        for i in self.curr_view_data.added_annot:
            self.view.listbox_steps.listbox.insert(tk.END, i)

        self.updatable_annot = updatable_annotation.get_instance_by_axes(self.ax)

        self.view.listbox_lines.delete_all()
        for i in self.curr_view_data.custom_lines_objs.keys():
            self.view.listbox_lines.listbox.insert(tk.END, i)

        self.view.sidepanel.set_droplist_values(self.curr_view_data.phases, self.curr_view_data.current_phase)

    def update_listbox_entry(self, line_obj):
        for k, v in self.curr_view_data.custom_lines_objs.items():
            if(v == line_obj):
                listbox_index = self.view.listbox_lines.listbox.get(0, "end").index(k)
                x = int(v.line.get_xdata()[0])
                old_key = k
                new_key = x
                break

        self.view.listbox_lines.update_item(listbox_index, x)
        self.curr_view_data.custom_lines_objs[new_key] = self.curr_view_data.custom_lines_objs[old_key]
        del self.curr_view_data.custom_lines_objs[old_key]
