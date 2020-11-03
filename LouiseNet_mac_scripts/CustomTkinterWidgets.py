"""
Custom Widgets used in application
(enables automatic resizing)
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font
import random
import time
from collections import defaultdict

DEFAULT_FONT = 'Roboto Light'
DEFAULT_RESIZE_DATA = {'class_instance': None,
                       'x_mul': 0.85,
                       'y_mul': 0.85,
                       'min_fs': 10,
                       'max_fs': 35}
all_font_widgets = defaultdict(lambda: [])
# --Constants--
WHITE = '#FFFFFF'
BLACK = '#000000'


class ResizeManager:
    DEFAULT_HZ = 10

    def __init__(self, parent: tk.Wm, resize_mode: str = 'manual'):
        self.parent = parent

        self.resizing_window = resize_mode
        self.current_resize_window = self.parent.__class__.__name__
        self.default_resize_data = defaultdict(lambda: DEFAULT_RESIZE_DATA.copy())  # nopep8
        self.window_widgets = defaultdict(lambda: [])
        self.wait_ms = self._convert_hz_ms(hz=self.DEFAULT_HZ)

        # -Set Default Resizing Settings-
        self.set_defaultResizeData(WidgetClass=Label,
                                   resize_data={'y_mul': 0.8, 'x_mul': 0.8})
        self.set_defaultResizeData(WidgetClass=Button,
                                   resize_data={'y_mul': 0.8, 'x_mul': 0.7})
        self.set_defaultResizeData(WidgetClass=Checkbutton,
                                   resize_data={'y_mul': 0.8, 'x_mul': 0.7})
        self.set_defaultResizeData(WidgetClass=Entry,
                                   resize_data={'y_mul': 0.8, 'x_mul': 0.7,
                                                'min_fs': 15, 'max_fs': 20})
        self.set_defaultResizeData(WidgetClass=Radiobutton,
                                   resize_data={'y_mul': 0.8, 'x_mul': 0.8,
                                                'min_fs': 10, 'max_fs': 20})

        self.performance_measures = []

    def start_resize_loop(self):
        """
        """
        def resize_loop():
            self.update_window()
            self.parent.after(self.wait_ms,
                              lambda: resize_loop())
        resize_loop()

    def update_window(self, window: tk.Wm = None):
        stime = time.perf_counter()
        global all_font_widgets
        widgets_to_resize, window = self._get_widgets_to_resize(window=window)

        for font_name, font_widgets in all_font_widgets.items():
            if font_widgets:
                longest_text_widget = None
                longest_text = ''
                for widget in font_widgets:
                    if widget.winfo_exists():
                        widget_text = widget._get_text()
                    else:
                        all_font_widgets[font_name].remove(widget)
                        continue
                    if not (widget in widgets_to_resize):
                        continue

                    if len(widget_text) > len(longest_text):
                        longest_text = widget_text
                        longest_text_widget = widget
                    else:
                        widget.update_wraplength()

                if longest_text_widget is not None:
                    widget_class_name = longest_text_widget.__class__.__name__
                    resize_data = self.default_resize_data[widget_class_name].copy()  # nopep8

                    if longest_text_widget.winfo_exists():
                        resize_data.update(longest_text_widget.resize_data)
                        longest_text_widget.fit_text(resize_data=resize_data)
                    else:
                        all_font_widgets[font_name].remove(longest_text_widget)
                        self.window_widgets[window].remove(widget)

        total_time = round(time.perf_counter() - stime, 5)
        self.performance_measures.append(total_time)

    def add_widget(self, widget: ttk.Widget, window: tk.Wm):
        """
        """
        window_class_name = window.__class__.__name__
        self.window_widgets[window_class_name].append(widget)

    def switch_resize_window(self, window: tk.Wm):
        """
        """
        self.current_resize_window = window.__class__.__name__
        self.update_window(window=window)

    def set_defaultResizeData(self, WidgetClass, resize_data: dict):
        """
        """
        widget_class_name = WidgetClass.__name__
        self.default_resize_data[widget_class_name].update(resize_data)

    def set_updateHz(self, hz):
        """
        """
        self.wait_ms = self._convert_hz_ms(hz=hz)

    def _get_widgets_to_resize(self, window: tk.Wm = None):
        if window is not None:
            window_name = window.__class__.__name__
            return self.window_widgets[window_name], window_name
        elif self.resizing_window == 'focus':
            focused_widget = self.parent.focus_get()
            focused_window_name: str

            if focused_widget is None:
                focused_window_name = self.parent.__class__.__name__
            else:
                focused_window_name = focused_widget.winfo_toplevel().__class__.__name__

            return self.window_widgets[focused_window_name], focused_window_name
        elif self.resizing_window == 'manual':
            return self.window_widgets[self.current_resize_window], self.current_resize_window

    def _convert_hz_ms(self, hz: int) -> int:
        """Convert hz to ms

        Paramtars:
            hz(int): hz to convert into ms
        """
        return int((1 / hz) * 1000)

    def __str__(self):
        return f'Average time to resize widgets: {round(sum(self.performance_measures)/len(self.performance_measures), 5)}s'  # nopep8


class CustomTkinterMethods:
    def __init__(self):
        self.last_fontsize = 0

    def fit_text(self, resize_data: dict) -> int:
        """
        Calculate the maximum fontsize which fits the text into the
        given width and height
        """
        BUFFER_PIXELS = 2
        # --Variables--
        text: str
        longest_line: str
        target_width: int
        target_height: int
        text_width: int
        text_height: int
        width_difference: float
        height_difference: float
        # --Approximate new Fontsize--
        padding = self._get_padding()
        # -Get text-
        text = self._get_text()
        if not text:
            return
        longest_line = max(text.split('\n'), key=len)
        target_width = max(self.winfo_width() * resize_data['x_mul'] - (padding*2),
                           25)
        target_height = max(self.winfo_height() * resize_data['y_mul'] - (padding*2),
                            25)
        text_width = self.font.measure(longest_line)
        text_height = self.font.metrics('linespace') * (text.count('\n') + 1)  # nopep8
        width_difference = ((target_width - BUFFER_PIXELS) / text_width)
        height_difference = ((target_height - BUFFER_PIXELS) / text_height)
        # Fontsize Approximation
        approx_fontsize = min(self.font.cget('size') * width_difference,
                              self.font.cget('size') * height_difference)
        approx_fontsize = min(resize_data['max_fs'], approx_fontsize)
        approx_fontsize = max(resize_data['min_fs'], approx_fontsize)

        if abs(self.last_fontsize - approx_fontsize) > 1:
            self.font.configure(size=int(approx_fontsize))
            self.last_fontsize = approx_fontsize

        self.update_wraplength()
        if isinstance(self, Entry):
            self.insert(0, ' ')
            self.delete(0)

        return self.font.cget('size')

    def update_wraplength(self):
        padding = self._get_padding()
        if isinstance(self, Label):
            self.configure(wraplength=self.winfo_width() - padding*2 - 15)
        if isinstance(self, Button):
            ttk.Style().configure(self.style, wraplength=self.winfo_width() - padding*2 - 15)

    @staticmethod
    def full_font(font) -> tk.font.Font:
        """
        Returns: Font
        """
        if isinstance(font, tk.font.Font):
            return font

        if isinstance(font, float):
            raise TypeError(
                f'full_font does not accept float\nGiven Font: {font}')

        # Only fontsize is given
        if (type(font) is int):
            return tk.font.Font(family=DEFAULT_FONT, size=font, weight=tk.font.NORMAL)
        # Font and fontsize is given
        elif (len(font) == 2):
            return tk.font.Font(family=font[0], size=font[1], weight=tk.font.NORMAL)
        # Everything is given
        elif (len(font) == 3):
            return tk.font.Font(family=font[0], size=font[1], weight=font[2])
        else:
            raise TypeError('Font options too long')

    def _get_text(self) -> str:
        text = ''

        if isinstance(self, Entry):
            text = self.get()
        elif isinstance(self, OptionMenu):
            text = str(self.variable.get())
        else:
            text = self.cget('text')

        return str(text)

    def _get_buffer(self) -> int:

        if isinstance(self, Label):
            buffer_pixels = 6
        elif isinstance(self, Button):
            buffer_pixels = 20
        elif isinstance(self, Checkbutton) or isinstance(self, Radiobutton):
            buffer_pixels = 24
        elif isinstance(self, Entry):
            buffer_pixels = 4
        else:
            buffer_pixels = 0
        return buffer_pixels

    def _get_actual_parent(self, parent=None):
        """
        """
        if isinstance(parent, ScrollableFrame):
            return parent.content
        elif parent is not None:
            return parent
        else:
            return tk._default_root

    def _get_padding(self) -> int:
        padding = 0
        try:
            # -Check Configure-
            padding_object = self.cget('padding')
            if padding_object:
                try:
                    padding = int(padding_object[0].string)
                except TypeError:
                    padding = padding_object
            # -Check Style-
            padding_object = ttk.Style().lookup(self.style, 'padding')
            if padding_object:
                try:
                    padding = int(padding_object[0].string)
                except TypeError:
                    padding = padding_object
        except tk.TclError as e:
            pass
        return padding


class Label(ttk.Label, CustomTkinterMethods):
    """
    Box which displays text

    Paramaters:
        parent:
            window in which the widgets will be displayed in
        text(str):
            text do display in the Label
        textvariable(tk.Variable):
            overrides text paramater. Dynamically change the text
            in this label by modifiying the variables value.
        font(tk.font):
            font type used by the text. When information is not given, the
            programm chooses the default values.
            Valid arguments are:
                - a tk.font instance
                - a list with a length of 3 [FONT FAMILY(str), FONT SIZE(int), FONT WEIGHT(str)]
                - a list with a length of 2 [FONT FAMILY(str), FONT SIZE(int)]
                - an int holding the font size
        resizer(ResizeManager):
            the resize manager this widget will be appended to.
        resize_data(dict):
            dictionary of values to manipulate the resizing.
            Valid keys are:
                'x_mul' = the text will fit itself into a box of its width * x_mul
                'y_mul' = the text will fit itself into a box of its height * y_mul
                'min_fs' = minimum fontsize
                'max_fs' = maximum fontsize
        style(str):
            style of the widget
        **kwargs:
            arguments which will passed in the inherited class
    """

    def __init__(self, parent=None, text: str = "ABC123", textvariable: tk.Variable = None,
                 font: tk.font = 10,
                 resizer: ResizeManager = None, resize_data: dict = {},
                 style: str = None, **kwargs):
        # --Save arguments--
        # -Default Variables-
        self.parent = self._get_actual_parent(parent)
        self.style = style if (style is not None) else "{0}.TLabel".format(random.randrange(0, 100_000))  # nopep8
        self.textvariable = textvariable
        self.font = self.full_font(font)
        self.resize_data = resize_data
        # -Class Specific Variables-
        # !Images

        # --Initialize Widget--
        CustomTkinterMethods.__init__(self)
        ttk.Label.__init__(self, master=self.parent,
                           text=text, textvariable=self.textvariable,
                           font=self.font,
                           style=self.style, **kwargs)
        ttk.Style().configure(self.style, font=self.font)

        # --Update Resize Data--
        if isinstance(resizer, ResizeManager):
            self.resizer = resizer
            self.resizer.add_widget(widget=self,
                                    window=self.winfo_toplevel())
            global all_font_widgets
            all_font_widgets[self.font.name].append(self)


class Button(ttk.Button, CustomTkinterMethods):
    """
    Button which executes its given command when pressed
    """

    def __init__(self, parent=None, text: str = "ABC123", textvariable: tk.Variable = None,
                 font: tk.font = 10,
                 resizer: ResizeManager = None, resize_data: dict = {},
                 command=(lambda: None), repeat_data: dict = {'delay': None, 'intervall': None},
                 style: str = None, **kwargs):
        # --Save arguments--
        # -Default Variables-
        self.parent = self._get_actual_parent(parent)
        self.style = style if (style is not None) else "{0}.TButton".format(random.randrange(0, 100_000))  # nopep8
        self.textvariable = textvariable
        self.font = self.full_font(font)
        self.resize_data = resize_data
        # -Class Specific Variables-
        self.command = command
        self.repeat_data = repeat_data
        self.current_loop = None

        # --Initialize Widget--
        CustomTkinterMethods.__init__(self)
        ttk.Button.__init__(self, master=self.parent,
                            text=text, textvariable=self.textvariable,
                            command=command,
                            style=self.style, **kwargs)
        ttk.Style().configure(self.style, font=self.font)
        self.bindKeys()

        # --Update Resize Data--
        if isinstance(resizer, ResizeManager):
            self.resizer = resizer
            self.resizer.add_widget(widget=self,
                                    window=self.winfo_toplevel())
            global all_font_widgets
            all_font_widgets[self.font.name].append(self)

    def bindKeys(self):
        # invoke -> Press Button
        self.bind("<Return>", (lambda e: self.after(50, self.invoke)))
        if (self.repeat_data['delay'] is not None and
                self.repeat_data['intervall'] is not None):
            self.bind("<Button-1>", (lambda e: self.start_repeat_loop()))  # nopep8
            self.bind("<ButtonRelease-1>", (lambda e: self.stop_repeat_loop()))  # nopep8
            self.configure(command=None)

    def start_repeat_loop(self):
        def invoke_button():
            self.command()
            self.current_loop = self.after(self.repeat_data['intervall'],
                                           invoke_button)

        self.current_loop = self.after(self.repeat_data['delay'],
                                       invoke_button)

    def stop_repeat_loop(self):
        self.after_cancel(self.current_loop)
        self.current_loop = None


class Checkbutton(ttk.Checkbutton, CustomTkinterMethods):
    """
    Create a button which can be turned ON or OFF with an indicator
    """

    def __init__(self, parent=None, text: str = "ABC123", textvariable: tk.Variable = None,
                 font: tk.font = 10,
                 resizer: ResizeManager = None, resize_data: dict = {},
                 command=(lambda: None), variable: tk.BooleanVar = None,
                 style: str = None, **kwargs):
        # --Save arguments--
        # -Default Variables-
        self.parent = self._get_actual_parent(parent)
        self.style = style if (style is not None) else "{0}.TCheckbutton".format(random.randrange(0, 100_000))  # nopep8
        self.textvariable = textvariable
        self.font = self.full_font(font)
        self.resize_data = resize_data
        # -Class Specific Variables-
        self.command = command
        self.variable = variable

        # --Initialize Widget--
        CustomTkinterMethods.__init__(self)
        ttk.Checkbutton.__init__(self, master=self.parent,
                                 text=text, textvariable=self.textvariable,
                                 command=command, variable=self.variable,
                                 style=self.style, **kwargs)
        ttk.Style().configure(self.style, font=self.font)
        self.bindKeys()

        # --Update Resize Data--
        if isinstance(resizer, ResizeManager):
            self.resizer = resizer
            self.resizer.add_widget(widget=self,
                                    window=self.winfo_toplevel())
            global all_font_widgets
            all_font_widgets[self.font.name].append(self)

    # Default Methods
    def bindKeys(self):
        """
        Bind Events to this widget
        """
        # invoke = Toggle Button
        self.bind("<Return>", (lambda event: self.after(50, self.invoke)))


class Entry(ttk.Entry, CustomTkinterMethods):
    """
    Create a field in which the user has the ability to type in text
    """

    def __init__(self, parent=None, text: str = '', textvariable: tk.Variable = None,
                 font: tk.font = 10,
                 resizer: ResizeManager = None, resize_data: dict = {},
                 check_validity_command=(lambda t: True), valid_command=(lambda w: None), not_valid_command=(lambda w: None),
                 style: str = None, **kwargs):
        # --Save arguments--
        # -Default Variables-
        self.parent = self._get_actual_parent(parent)
        self.style = style if (style is not None) else "{0}.TEntry".format(random.randrange(0, 100_000))  # nopep8
        self.textvariable = textvariable if textvariable is not None else tk.StringVar(value=text)  # nopep8
        self.font = self.full_font(font)
        self.resize_data = resize_data
        # -Class Specific Variables-
        self.check_valid_entry = check_validity_command
        self.valid_command = valid_command
        self.not_valid_command = not_valid_command

        # --Initialize Widget--
        CustomTkinterMethods.__init__(self)
        ttk.Entry.__init__(self, master=self.parent,
                           textvariable=self.textvariable,
                           font=self.font,
                           style=self.style, **kwargs)
        self.bindKeys()

        # --Update Resize Data--
        if isinstance(resizer, ResizeManager):
            self.resizer = resizer
            self.resizer.add_widget(widget=self,
                                    window=self.winfo_toplevel())
            global all_font_widgets
            all_font_widgets[self.font.name].append(self)

    def bindKeys(self):
        """
        Bind Events to this widget
        """
        self.bind("<FocusOut>", self.update)
        self.bind("<FocusOut>", (lambda e: self.selection_clear()), add="+")
        if self.textvariable is not None:
            self.textvariable.trace('w', (lambda name, index, mode: self.update()))  # nopep8

    def update(self, event=None):
        """
        Run the valid or notvalid Command depending on the validity of the Entry
        """
        # Run the valid or not valid command
        if (self.check_valid_entry(self.cget('text'))):
            self.valid_command(self)
        else:
            self.not_valid_command(self)


class Radiobutton(ttk.Radiobutton, CustomTkinterMethods):
    """
    Button which only allows one of its group to be selected

    variable: tk value holder (StringVar, IntVar, ...)\n
    value: how to store this widget in the variable when it is selected
    """

    def __init__(self, parent=None, text: str = '', textvariable: tk.Variable = None,
                 font: tk.font = 10,
                 resizer: ResizeManager = None, resize_data: dict = {},
                 variable: tk.Variable = None, value=None, command=(lambda: None),
                 style: str = None, **kwargs):

        # --Save arguments--
        # -Default Variables-
        self.parent = self._get_actual_parent(parent)
        self.style = style if (style is not None) else "{0}.TRadiobutton".format(random.randrange(0, 100_000))  # nopep8
        self.textvariable = textvariable if textvariable is not None else tk.StringVar(value=text)  # nopep8
        self.font = self.full_font(font)
        self.resize_data = resize_data
        # -Class Specific Variables-
        self.variable = variable if (variable is not None) else tk.StringVar()
        self.value = value if (variable is not None) else 0  # nopep8
        self.command = command

        # --Initialize Widget--
        CustomTkinterMethods.__init__(self)
        ttk.Radiobutton.__init__(self, master=self.parent,
                                 textvariable=self.textvariable,
                                 variable=self.variable, value=self.value, command=self.command,
                                 style=self.style, **kwargs)
        ttk.Style().configure(self.style, font=self.font)
        self.bindKeys()

        # --Update Resize Data--
        if isinstance(resizer, ResizeManager):
            self.resizer = resizer
            self.resizer.add_widget(widget=self,
                                    window=self.winfo_toplevel())
            global all_font_widgets
            all_font_widgets[self.font.name].append(self)

    def bindKeys(self):
        # invoke -> Press Button
        self.bind("<Return>", (lambda event: self.invoke()))


class OptionMenu(ttk.OptionMenu, CustomTkinterMethods):
    def __init__(self, parent=None,
                 font: tk.font = 10,
                 variable: tk.Variable = None, values: list = [1, 2, 3], default=None,
                 resizer: ResizeManager = None, resize_data: dict = {},
                 style: str = None, **kwargs):
        # --Save arguments--
        # -Default Variables-
        self.parent = self._get_actual_parent(parent)
        self.style = style if (style is not None) else "{0}.Horizontal.TMenubutton".format(random.randrange(0, 100_000))  # nopep8
        self.font = self.full_font(font)
        self.resize_data = resize_data
        # -Class Specific Variables-
        self.variable = variable if (variable is not None) else tk.StringVar()
        self.values = values

        # --Initialize Widget--
        CustomTkinterMethods.__init__(self)
        ttk.OptionMenu.__init__(self,
                                self.parent,
                                self.variable,
                                default,
                                *self.values,
                                **kwargs)
        self.configure(style=self.style)
        ttk.Style().configure(self.style, font=self.font)

        # --Update Resize Data--
        if isinstance(resizer, ResizeManager):
            self.resizer = resizer
            self.resizer.add_widget(widget=self,
                                    window=self.winfo_toplevel())
            global all_font_widgets
            all_font_widgets[self.font.name].append(self)


class Progressbar(ttk.Progressbar, CustomTkinterMethods):
    def __init__(self, parent=None, orient: str = 'horizontal',
                 variable: tk.Variable = None, maximum: int = 100,
                 style: str = None, **kwargs):
        # --Save arguments--
        # -Default Variables-
        self.parent = self._get_actual_parent(parent)
        self.style = style if (style is not None) else "{0}.{1}.TProgressbar".format(random.randrange(0, 100_000), orient.capitalize())  # nopep8
        # -Class Specific Variables-
        self.variable = variable if (variable is not None) else tk.IntVar()
        self.orient = orient
        self.maximum = maximum

        # --Initialize Widget--
        CustomTkinterMethods.__init__(self)
        ttk.Progressbar.__init__(self, master=self.parent,
                                 orient=self.orient,
                                 variable=self.variable, maximum=self.maximum,
                                 style=self.style, **kwargs)


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, scroll_side: str = None, **kwargs):
        # --Variables--
        self.scroll_width = 17  # Scrollbar width
        self.scrollable_height = 0
        self.scrollable_width = 0

        super().__init__(master=parent,
                         **kwargs)

        # --Create Widgets--
        self.canvas = tk.Canvas(self, borderwidth=0,
                                highlightthickness=0)
        # Holds all widgets
        self.content = tk.Frame(master=self.canvas)
        self.scrollbar_Y = tk.Scrollbar(self,
                                        orient='vertical',
                                        width=self.scroll_width)
        self.scrollbar_X = tk.Scrollbar(self,
                                        orient='horizontal',
                                        width=self.scroll_width)
        # Put self.content on the canvas
        self.canvas_window = self.canvas.create_window((1, 1),
                                                       window=self.content,
                                                       anchor="nw")

        canvas_x = 0
        canvas_y = 0
        canvas_width = 0
        canvas_height = 0
        if 'n' in scroll_side:
            scroll_x = tk.TOP
            # Canvas Placement
            canvas_y = self.scroll_width
            canvas_height = -self.scroll_width
        elif 's' in scroll_side:
            scroll_x = tk.BOTTOM
            # Canvas Placement
            canvas_height = -self.scroll_width
        if 'e' in scroll_side:
            scroll_y = tk.RIGHT
            # Canvas Placement
            canvas_width = -self.scroll_width
        elif 'w' in scroll_side:
            scroll_y = tk.LEFT
            canvas_x = self.scroll_width
            canvas_width = -self.scroll_width

        # -Manage placement of scrollbars-
        if scroll_y == tk.LEFT:
            if scroll_x == tk.TOP:
                place_x = {'x': self.scroll_width, 'y': 0, 'width': -self.scroll_width, 'height': self.scroll_width,
                           'relx': 0, 'rely': 0, 'relwidth': 1, 'relheight': 0}
                place_y = {'x': 0, 'y': self.scroll_width, 'width': self.scroll_width, 'height': -self.scroll_width,
                           'relx': 0, 'rely': 0, 'relwidth': 0, 'relheight': 1}
            elif scroll_x == tk.BOTTOM:
                place_x = {'x': self.scroll_width, 'y': -self.scroll_width, 'width': -self.scroll_width, 'height': self.scroll_width,
                           'relx': 0, 'rely': 1, 'relwidth': 1, 'relheight': 0}
                place_y = {'x': 0, 'y': 0, 'width': self.scroll_width, 'height': -self.scroll_width,
                           'relx': 0, 'rely': 0, 'relwidth': 0, 'relheight': 1}
        elif scroll_y == tk.RIGHT:
            if scroll_x == tk.TOP:
                place_x = {'x': 0, 'y': 0, 'width': -self.scroll_width, 'height': self.scroll_width,
                           'relx': 0, 'rely': 0, 'relwidth': 1, 'relheight': 0}
                place_y = {'x': -self.scroll_width, 'y': self.scroll_width, 'width': self.scroll_width, 'height': -self.scroll_width,
                           'relx': 1, 'rely': 0, 'relwidth': 0, 'relheight': 1}
            elif scroll_x == tk.BOTTOM:
                place_x = {'x': 0, 'y': -self.scroll_width, 'width': -self.scroll_width, 'height': self.scroll_width,
                           'relx': 0, 'rely': 1, 'relwidth': 1, 'relheight': 0}
                place_y = {'x': -self.scroll_width, 'y': 0, 'width': self.scroll_width, 'height': -self.scroll_width,
                           'relx': 1, 'rely': 0, 'relwidth': 0, 'relheight': 1}

        # --Place Widgets--
        self.scrollbar_Y.place(place_y)
        self.scrollbar_X.place(place_x)
        self.canvas.place(x=canvas_x, y=canvas_y, width=canvas_width, height=canvas_height,
                          relx=0, rely=0, relwidth=1, relheight=1)

        # --Configure Widgets--
        self.scrollbar_Y.configure(command=self.canvas.yview)
        self.scrollbar_X.configure(command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.scrollbar_Y.set,
                              xscrollcommand=self.scrollbar_X.set)
        # --Bind Widgets--
        self.content.bind("<Configure>", (lambda e: self.update_scrollregion()))  # nopep8
        self.canvas.bind("<Configure>", (lambda e: self.fit_content()))
        self.bind("<MouseWheel>", self.scroll)
        self.canvas.bind("<MouseWheel>", self.scroll)
        self.content.bind("<MouseWheel>", self.scroll)

        if 'background' in kwargs.keys():
            self.canvas.configure(background=kwargs['background'])
            self.content.configure(background=kwargs['background'])

    def update_scrollregion(self):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def fit_content(self):
        """Resize MultiFrame to fit all widgets"""
        self.canvas.itemconfig(self.canvas_window, width=self._get_scrollWidth(), height=self._get_scrollHeight())  # nopep8

    def _get_scrollHeight(self) -> int:
        """Find scrollable height"""
        height = 0
        for widget in self.content.winfo_children():
            height = max(height, widget.winfo_y() + widget.winfo_height())

        return height

    def _get_scrollWidth(self) -> int:
        """Find scrollable width"""
        width = 0
        for widget in self.content.winfo_children():
            width = max(width, widget.winfo_x() + widget.winfo_width())

        return width

    def scroll(self, event):
        """Scroll the widget"""

        STEPS = 0.025
        scroll_down = event.delta < 0

        # INFO If wanting to invert scroll directions invert the
        # INFO return statements as well as the STEP Functions

        # Gives True when the Top or Bottom end of the slider hits the end
        if ((not scroll_down and self.canvas.yview()[0] == 0) or
                (scroll_down and self.canvas.yview()[1] == 1)):
            return

        y0 = self.canvas.yview()[0]
        y0 += STEPS if (scroll_down) else -STEPS

        self.canvas.yview_moveto(y0)


def create_style():
    # -Style Settings-
    ttk.Style().theme_create('CustomTheme', 'classic')  # , 'vista')
    ttk.Style().theme_use('CustomTheme')
    ttk.Style().element_create('Windows.Button.focus', 'from', 'vista', 'Button.focus')
    ttk.Style().element_create('Windows.Radiobutton.indicator', 'from', 'vista', 'Radiobutton.indicator')  # nopep8
    ttk.Style().element_create('Windows.Checkbutton.indicator', 'from', 'vista', 'Checkbutton.indicator')  # nopep8
    ttk.Style().element_create('Windows.Horizontal.Progressbar.trough', 'from', 'vista', 'Horizontal.Progressbar.trough')  # nopep8
    ttk.Style().element_create('Windows.Horizontal.Progressbar.pbar', 'from', 'vista', 'Horizontal.Progressbar.pbar')  # nopep8
    ttk.Style().element_create('Windows.Vertical.Progressbar.trough', 'from', 'vista', 'Vertical.Progressbar.trough')  # nopep8
    ttk.Style().element_create('Windows.Vertical.Progressbar.pbar', 'from', 'vista', 'Vertical.Progressbar.pbar')  # nopep8
    ttk.Style().theme_settings('CustomTheme', {
        '.': {
            'configure': {
                'font': (DEFAULT_FONT, 10),
                'background': WHITE,
                'foreground': BLACK,
                'justify': tk.CENTER,
                'anchor': tk.CENTER,
            }
        },
        'TCheckbutton': {
            'configure': {
                'padding': 2,
                'anchor': tk.W,
                'justfiy': tk.LEFT,
            },
            'layout': [(
                'Checkbutton.highlight', {
                    'sticky': 'nswe',
                    'children': [(

                        'Checkbutton.border', {
                            'sticky': 'nswe',
                            'children': [(

                                'Checkbutton.padding', {
                                    'sticky': 'nswe',
                                    'children': [(
                                        'Windows.Checkbutton.indicator', {
                                            'side': 'left',
                                            'sticky': ''
                                        }),
                                        ('Checkbutton.label', {
                                            'side': 'left',
                                            'sticky': 'nswe'
                                        }
                                    )]
                                }
                            )]
                        }
                    )]
                }
            )]
        },
        'Custom.TCheckbutton': {
            'configure': {
                'highlightthickness': 1,
                'padding': 2,
                'anchor': tk.CENTER
            },
            'map': {
                'foreground': [('selected', '#005400'),
                               ('!selected', '#740000')],
                'background': [('pressed', '#FFFFFF'),
                               ('active', 'selected', '#E6FBE6'),
                               ('active', '!selected', '#FFEAEA'),
                               ('selected', '#D1F7D1'),
                               ('!selected', '#FFD1D1')],
                'highlightcolor': [('selected', '#007400'),
                                   ('!selected', '#FF4646')],
            },
            'layout': [(
                'Checkbutton.highlight', {
                    'sticky': 'nswe',
                    'children': [(

                        'Checkbutton.border', {
                            'sticky': 'nswe',
                            'children': [(

                                'Checkbutton.padding', {
                                    'sticky': 'nswe',
                                    'children': [(

                                        'Checkbutton.label', {
                                            'sticky': 'nswe',
                                        }
                                    )]
                                }
                            )]
                        }
                    )]
                }
            )]
        },
        # Windows Button Emulation
        'TButton': {
            'configure': {
                'background': '#E1E1E1',
                'highlightcolor': '#ADADAD',
                'highlightthickness': 1,
                'padding': 1,
                'anchor': tk.CENTER,
                'justify': tk.CENTER,
            },
            'map': {
                'background': [('pressed', '#CCE4F7'),
                               ('active', '#E5F1FB')],
                'highlightcolor': [('pressed', '#005499'),
                                   ('active', '#0078D7')],
            },

            'layout': [(
                'Button.highlight', {
                    'sticky': 'nsew',
                    'children': [(

                        'Button.button', {
                            'sticky': 'nswe',
                            'children': [(

                                'Button.padding', {
                                    'sticky': 'nswe',
                                    'children': [(
                                        'Windows.Button.focus', {
                                            'sticky': 'nswe',
                                            'children': [(
                                                'Button.label', {
                                                    'sticky': 'nswe',
                                                }
                                            )]
                                        }
                                    )]
                                }
                            )]
                        }
                    )]
                }
            )]
        },
        'Custom.TButton': {
            'configure': {
                'background': '#F5FAFE',
                'foreground': '#006CE0',
                'highlightcolor': '#0072BE',
                'highlightthickness': 1,
                'padding': 1,
                'anchor': tk.CENTER,
                'justify': tk.CENTER,
            },
            'map': {
                'background': [('pressed', '#D1ECFF'),
                               ('active', '#E1F2FF')],
                'highlightcolor': [('focus', '#0072BE'),
                                   ('active', '#0078D7')],
            },

            'layout': [(
                'Button.highlight', {
                    'sticky': 'nsew',
                    'children': [(

                        'Button.button', {
                            'sticky': 'nswe',
                            'children': [(

                                'Button.padding', {
                                    'sticky': 'nswe',
                                    'children': [(

                                        'Button.label', {
                                            'sticky': 'nswe',
                                        }
                                    )]
                                }
                            )]
                        }
                    )]
                }
            )]
        },
        'TEntry': {
            'configure': {
                'fieldbackground': WHITE,
                'selectbackground': '#0078D7',
                'selectforeground': WHITE,
                'highlightcolor': '#7A7A7A',
                'padding': 3,
                'highlightthickness': 1,
                'borderwidth': 0,
            },
            'map': {
                'highlightcolor': [('focus', '#0078D7'), ],
            },
        },
        'TRadiobutton': {
            'configure': {
                'padding': 3,
                'borderwidth': 0,
                'anchor': tk.W,
                'justify': tk.LEFT,
            },
            'map': {},

            'layout': [(
                'Radiobutton.highlight', {
                    'sticky': 'nswe',
                    'children': [(

                        'Radiobutton.border', {
                            'sticky': 'nswe',
                            'children': [(

                                'Radiobutton.padding', {
                                    'sticky': 'nswe',
                                    'children': [(
                                        'Windows.Radiobutton.indicator', {
                                            'side': 'left',
                                            'sticky': '',
                                        }),
                                        ('Radiobutton.padding', {
                                            'sticky': 'nswe',
                                            'children': [(
                                                'MyRadiobutton.label', {
                                                    'sticky': 'nswe',
                                                }
                                            )]
                                        }
                                    )]
                                }
                            )]
                        }
                    )]
                }
            )]
        },
        'Custom.TRadiobutton': {
            'configure': {
                'background': '#F5FAFE',
                'foreground': '#006FB9',
                'padding': 3,
                'borderwidth': 0,
                'anchor': tk.W,
                'justify': tk.LEFT,
            },
            'map': {
                'background': [('selected', '#B2E0FF'),
                               ('active', '#D5EEFF'),
                               ('focus', '#D5EEFF')],
                'highlightthickness': [('focus', 1),
                                       ('!focus', 0)
                                       ],
                'highlightcolor': [('focus', '#0072BE'),
                                   ('!focus', WHITE)
                                   ],
            },

            'layout': [(
                'Radiobutton.highlight', {
                    'sticky': 'nswe',
                    'children': [(

                        'Radiobutton.border', {
                            'sticky': 'nswe',
                            'children': [(

                                'Radiobutton.padding', {
                                    'sticky': 'nswe',
                                    'children': [(
                                        'MyRadiobutton.label', {
                                            'sticky': 'nswe',
                                        }
                                    )]
                                }
                            )]
                        }
                    )]
                }
            )]
        },
        'Horizontal.TProgressbar': {
            'configure': {
                'troughcolor': WHITE
            },
            'map': {

            },
            'layout': [(
                'Windows.Horizontal.Progressbar.trough', {
                    'sticky': 'nswe',
                    'children': [(
                        'Windows.Horizontal.Progressbar.pbar', {
                            'side': 'left',
                            'sticky': 'ns'
                        }
                    )]
                }
            )]
        },
        'DarkTheme.Horizontal.TProgressbar': {
            'configure': {
                'troughcolor': '#212121',
                'troughrelief': tk.FLAT,
                'pbarrelief': tk.FLAT,
                'background': '#BB86FC',
            },
            'map': {

            },
            'layout': [(
                'Horizontal.Progressbar.trough', {
                    'sticky': 'nswe',
                    'children': [(
                        'Horizontal.Progressbar.pbar', {
                            'side': 'left',
                            'sticky': 'ns'
                        }
                    )]
                }
            )]
        },
        'Vertical.TProgressbar': {
            'configure': {
                'troughcolor': WHITE
            },
            'map': {

            },
            'layout': [(
                'Windows.Vertical.Progressbar.trough', {
                    'sticky': 'nswe',
                    'children': [(
                        'Windows.Vertical.Progressbar.pbar', {
                            'side': 'left',
                            'sticky': 'ns'
                        }
                    )]
                }
            )]
        }
    })
    ttk.Style().theme_use('CustomTheme')
