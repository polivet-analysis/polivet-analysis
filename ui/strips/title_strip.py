import logging
from tkinter import *
from PIL import ImageTk
from PIL import Image as PilImage
from tkinter.filedialog import askopenfilename
from .image import resize_keep_ratio


class Strip:
    def __init__(self, y_position, height, color_scheme):
        self.y_position = y_position
        self.height = height
        self.color_scheme = color_scheme
        self.continue_callback = None
        self.log = logging.getLogger("TitleStrip")

    def set_continue_callback(self, callback):
        self.continue_callback = callback
        return self

    def create_layer(self, outer_frame):
        self.log.info("Creating title frame")
        self.frame = Frame(master=outer_frame, height=self.height,
                           bg=self.color_scheme.background_bright)
        self.frame.place(x=0, y=0, relwidth=1)

        self.left_frame = Frame(self.frame, height=self.height, bg=self.color_scheme.background_neutral)
        self.left_frame.place(x=0, y=0, relwidth=.66, anchor='nw')

        self.description = Text(self.left_frame, height=10,
                                bg=self.color_scheme.background_neutral,
                                foreground=self.color_scheme.text,
                                borderwidth=0, wrap=WORD,
                                padx=10, pady=10, spacing2=7)
        self.description.tag_configure("bold", font='Helvetica 14 bold',
                                       foreground=self.color_scheme.text_header)
        self.description.tag_configure("regular", font='Helvetica 12')
        self.description.insert(END, "АНАЛИЗ ДВИЖЕНИЯ ЧАСТИЦ\n\n", "bold")
        self.description.insert(END, "Расчет статистических характеристик движения частиц "
                                     "под микроскопом на основе видео. Чтобы начать работу, "
                                     "откройте видеофайл *.mp4"
                                , "regular")
        self.description.place(relx=.5, rely=.48, relwidth=.8, anchor='c')

        self.underscore = Canvas(self.left_frame, height=2, borderwidth=0, highlightthickness=0,
                                 bg=self.color_scheme.background_bright)
        self.underscore.place(relx=1, y=60, relwidth=.9, anchor='e')

        self.right_frame = Frame(self.frame, height=self.height, bg=self.color_scheme.background_bright)
        self.right_frame.place(relx=1, y=0, relwidth=.33, anchor='ne')

        self.button = Button(self.right_frame, width=20, height=2,
                             bg=self.color_scheme.background_light,
                             fg=self.color_scheme.text_header,
                             disabledforeground=self.color_scheme.text_disabled,
                             borderwidth=0, cursor='hand2',
                             font=('Helvetica', 10, 'bold'),
                             text='OPEN')
        self.button.bind("<Button-1>", lambda e: self.__start_loading())
        self.button.place(relx=.5, rely=.7, anchor='c')

        self.data_icon = PilImage.open('resources/misc/data-analytics-icon-t.png')
        self.data_icon = resize_keep_ratio(self.data_icon, 100)
        self.icon_canvas = Canvas(self.right_frame, width=self.data_icon.size[0],
                                  height=self.data_icon.size[0],
                                  borderwidth=0, highlightthickness=0,
                                  bg=self.color_scheme.background_bright)
        self.icon_canvas.place(relx=.5, rely=.3, anchor='c')
        self.data_icon = ImageTk.PhotoImage(image=self.data_icon)
        self.icon_canvas.create_image(0, 0, image=self.data_icon, anchor='nw')

        self.log.debug("Frame created")
        return self

    def __start_loading(self):
        if self.button['state'] == DISABLED:
            return

        self.log.info("Opening file dialog")
        f_name = askopenfilename(filetypes=[("Video files", ".mp4")])
        if f_name is not None and f_name:
            self.button["state"] = DISABLED
            self.continue_callback(f_name)
