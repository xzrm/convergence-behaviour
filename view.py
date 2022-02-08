from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os


class View:
    def __init__(self, master):
        self.top_frame = tk.Frame(master)
        self.sidepanel_frame = tk.Frame(master)
        self.plot_frame = tk.Frame(master)
        self.acc_frame = tk.Frame(master)

        self.top_frame.grid(column=0, row=0)
        self.plot_frame.grid(column=0, row=1, rowspan=2)

        self.plotview = PlotView(self.plot_frame)
        self.sidepanel = SidePanel(self.sidepanel_frame)
        self.menubar = MenuBar(master)

        self.acc_frame.grid(column=1, row=1, sticky="N", pady=5)
        self.acc = Accordion(self.acc_frame)
        self.settings_chord = Chord(self.acc, title="Analysis settings")
        self.annot_listbox_chord = Chord(self.acc, title="Add step")
        self.lines_listbox_chord = Chord(self.acc, title="Add line")

        # Label(self.first_chord, text='hello world', bg='white').pack()

        self.sidepanel = SidePanel(self.settings_chord)
        self.listbox_steps = StepListbox(self.annot_listbox_chord)
        self.listbox_lines = StepListbox(self.lines_listbox_chord)

        self.acc.append_chords(
            [self.settings_chord, self.annot_listbox_chord, self.lines_listbox_chord]
        )
        self.acc.pack(fill="both", expand=1, side=tk.TOP)

        self.listbox_steps.add_button.config(text="add step info")
        self.listbox_lines.add_button.config(text="add line")


class PlotView:
    tabs_content = {}

    def __init__(self, root):
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill="both")

    def add_tab(self):
        self.tab = ttk.Frame(self.notebook)

        self.notebook.add(self.tab, text="New")

        self.fig = Figure(figsize=(9, 5), dpi=80)
        self.ax = self.fig.add_axes((0.08, 0.08, 0.90, 0.90), frameon=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.tab)

        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.draw()
        self.tabs_content[self.notebook.tabs()[-1].split(".")[3]] = self.ax
        return self.tab

    def get_current_tab_obj(self):
        curr_tab = self.notebook.select()
        return curr_tab

    def delete_selected_tab(self):
        curr_tab = self.notebook.select().split(".")[3]
        del self.tabs_content[curr_tab]
        for item in self.notebook.winfo_children():
            if str(item) == self.notebook.select():
                item.destroy()
                return


class SidePanel:
    def __init__(self, root):
        self.frame = tk.Frame(root, borderwidth=1)
        self.frame.grid(column=0, row=0, padx=10, pady=10)

        self.phase_label = tk.Label(self.frame, text="Phase labels:")
        self.phase_label.grid(column=0, row=0, sticky="N")
        self.phase_droplist = ttk.Combobox(self.frame, values=[])
        self.phase_droplist.grid(columnspan=2, row=1, sticky="N", padx=5, pady=5)

        self.norm_label = tk.Label(self.frame, text="Select norm:")
        self.norm_label.grid(column=0, row=2, sticky="NW")
        self.norm_droplist = ttk.Combobox(
            self.frame, values=["displacement", "force", "energy"]
        )
        self.norm_droplist.current(0)
        print(self.norm_droplist.current(0))
        self.norm_droplist.grid(columnspan=2, row=3, sticky="N", padx=5, pady=5)

        self.tolerance_label = tk.Label(self.frame, text="Tolerance:")
        self.tolerance_label.grid(column=0, row=4, sticky="W", pady=5)
        self.tolerance_entry = tk.Entry(self.frame, width=10)
        self.tolerance_entry.insert(0, "0.01")
        self.tolerance_entry.grid(column=1, row=4, padx=5, pady=5)

        self.plot_button = tk.Button(self.frame, text="Plot")
        self.plot_button.grid(columnspan=2, row=5, padx=5, pady=5)
        self.clear_button = tk.Button(self.frame, text="Clear")
        self.clear_button.grid(columnspan=2, row=6)

    def set_droplist_values(self, values, display_value=None):
        self.phase_droplist["values"] = values

        if display_value:
            self.phase_droplist.set(display_value)
        else:
            self.phase_droplist.set("")

    def get_droplist_values(self):
        return self.phase_droplist["values"]

    def update_droplist_values(self, values):
        self.phase_droplist.set(" ")
        self.set_droplist_values(values)


class MenuBar:
    def __init__(self, root):
        self.menubar = tk.Menu(root)
        self.menu = tk.Menu(self.menubar, tearoff=0)
        # self.menu.add_command(label="Read file", command=self.read_file)
        self.menu.add_command(label="New")
        self.menu.add_command(label="Close")
        self.menu.add_command(label="Read file")
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=root.quit)

        self.menubar.add_cascade(label="File", menu=self.menu)

        self.initial_path = os.getcwd()
        root.config(menu=self.menubar)

    def read_file(self):

        file_name = filedialog.askopenfilename(
            initialdir=self.initial_path,
            filetypes=((".Out File", "*.out"), ("All Files", "*.*")),
            title="Choose a file",
        )
        self.initial_path = os.path.dirname(file_name)
        return file_name


class FilepathField:
    text = "File: "

    def __init__(self, root):
        self.frame = tk.Frame(root)
        self.frame.grid(column=0, row=0, padx=10, pady=0, sticky="W")
        self.text_field = tk.Text(self.frame, height=1, width=90)

        self.text_field.insert(tk.INSERT, self.text)
        self.text_field.grid()

    def refresh(self, new_text):

        self.filepath_field.delete("1.0", "end")
        self.filepath_field.insert(tk.INSERT, new_text)


class Chord(tk.Frame):
    """Tkinter Frame with title argument"""

    def __init__(self, parent, title="", *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        self.title = title


class Accordion(tk.Frame):
    chords_list = []

    def __init__(self, parent, accordion_style=None):
        tk.Frame.__init__(self, parent)

        # if no style dict, assign default style
        if accordion_style:
            self.style = accordion_style
        else:
            self.style = accordion_style = {
                "title_bg": "ghost white",
                "title_fg": "black",
                "highlight": "white smoke",
            }

        self.columnconfigure(0, weight=1)

    def append_chords(self, chords=[]):

        self.update_idletasks()
        row = 0
        width = max([c.winfo_reqwidth() for c in chords])

        for c in chords:
            self.chords_list.append(c)
            i = tk.PhotoImage()  # blank image to force Label to use pixel size
            label = tk.Label(
                self,
                text=c.title,
                image=i,
                compound="center",
                width=width,
                bg=self.style["title_bg"],
                fg=self.style["title_fg"],
                bd=2,
                relief="groove",
            )

            label.grid(row=row, column=0)
            c.grid(row=row + 1, column=0, sticky="N")
            c.grid_remove()
            row += 2

            label.bind("<Button-1>", lambda e, c=c: self.toggle_handler(c))
            label.bind(
                "<Enter>",
                lambda e, label=label, i=i: label.config(bg=self.style["highlight"]),
            )
            label.bind(
                "<Leave>",
                lambda e, label=label, i=i: label.config(bg=self.style["title_bg"]),
            )

    def toggle_handler(self, chord):
        for c in self.chords_list:
            if c.grid_info() != 0 and c != chord:
                c.grid_remove()

        if len(chord.grid_info()) == 0:
            chord.grid()
        else:
            chord.grid_remove()


class StepListbox:
    def __init__(self, root):
        self.frame = tk.Frame(root)
        self.frame.grid(pady=2)
        self.content = tk.StringVar()
        self.step_number_entry = tk.Entry(
            self.frame, width=20, textvariable=self.content
        )
        self.step_number_entry.grid(row=0, padx=(10, 0), pady=5)

        self.add_button = tk.Button(self.frame, text="Add")
        self.add_button.grid(row=1, column=0, pady=5)

        self.listbox = tk.Listbox(self.frame, width=20, height=5, selectmode="multiple")
        self.listbox.grid(row=2, column=0, padx=(10, 0), pady=(0, 5))

        self.scrollbar = tk.Scrollbar(
            self.frame, orient="vertical", command=self.listbox.yview
        )

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=2, column=1, sticky="NS", pady=(0, 5))

        self.delete_selected_button = tk.Button(self.frame, text="Delete selection")
        self.delete_selected_button.grid(row=3, column=0, pady=(0, 5))

    def add_value(self):
        value = self.content.get()
        if (value.isdigit()) and int(value) not in self.listbox.get(0, tk.END):
            self.listbox.insert(tk.END, int(value))
            return value

    def clear_text(self):
        self.step_number_entry.delete(0, tk.END)

    def delete_all(self):
        self.listbox.delete(0, tk.END)

    def delete_selected(self):
        deleted = []
        selected_items = self.listbox.curselection()
        # print(selected_items)
        for item in selected_items[::-1]:
            deleted.append(self.listbox.get(item))
            self.listbox.delete(item)
        return deleted

    def update_item(self, item_index, value):
        self.listbox.delete(item_index)
        self.listbox.insert(item_index, value)

    def delete_by_value(self, value):
        idx = self.listbox.get(0, tk.END).index(int(value))
        self.listbox.delete(idx)
