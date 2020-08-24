import logging
from tkinter import *
from PIL import Image, ImageTk
from .progress_bar import ProgressBar
from .thread import IterativeBackgroundTask
from .image import resize_keep_ratio


class Strip:
    def __init__(self, y_position, height, color_scheme, model):
        self.y_position = y_position
        self.height = height
        self.color_scheme = color_scheme
        self.model = model
        self.continue_callback = None
        self.log = logging.getLogger("VideoLoad")

    def set_continue_callback(self, callback):
        self.continue_callback = callback
        return self

    def create_layer(self, outer_frame):
        self.log.info("Creating frame")
        self.frame = Frame(master=outer_frame, height=self.height,
                           bg=self.color_scheme.background_neutral)
        self.frame.place(x=0, y=self.y_position, relwidth=1)

        # RIGHT FRAME

        self.right_frame = Frame(self.frame, height=self.height,
                                 bg=self.color_scheme.background_neutral)
        self.right_frame.place(x=0, y=0, relwidth=.4, anchor='nw')

        self.preview_canvas = Canvas(self.right_frame, height=200, highlightthickness=2,
                                     highlightbackground=self.color_scheme.background_dark)
        self.preview_canvas.place(relx=.1, rely=.48, anchor='w')
        self.__update_preview_canvas()

        # CENTER FRAME

        self.center_panel = Frame(self.frame, height=self.height,
                                  bg=self.color_scheme.background_neutral)
        self.center_panel.place(relx=.48, rely=0, relwidth=.16, anchor='n')

        self.brightness_slider = Scale(self.center_panel, from_=-500, to=500,
                                       sliderrelief=FLAT,
                                       background=self.color_scheme.background_neutral,
                                       foreground=self.color_scheme.text_header,
                                       borderwidth=1, highlightthickness=0, cursor='hand2',
                                       command=lambda b: self.__update_preview_canvas(b=b))
        self.brightness_slider.set(-300)
        self.brightness_slider.place(relx=.3, rely=.425, anchor='c', relheight=.7)

        self.brightness_label = Label(self.center_panel, text='ЯРКОСТЬ',
                                      font=('Helvetica', 9, 'bold'),
                                      bg=self.color_scheme.background_neutral,
                                      fg=self.color_scheme.text_header)
        self.brightness_label.place(relx=.35, rely=.85, anchor='c')

        self.contrast_slider = Scale(self.center_panel, from_=1, to=7, resolution=0.1,
                                     sliderrelief=FLAT,
                                     background=self.color_scheme.background_neutral,
                                     foreground=self.color_scheme.text_header,
                                     borderwidth=1, highlightthickness=0, cursor='hand2',
                                     command=lambda c: self.__update_preview_canvas(c=c))
        self.contrast_slider.set(4)
        self.contrast_slider.place(relx=.7, rely=.425, anchor='c', relheight=.7)

        self.contrast_label = Label(self.center_panel, text='КОНТРАСТ',
                                    font=('Helvetica', 9, 'bold'),
                                    bg=self.color_scheme.background_neutral,
                                    fg=self.color_scheme.text_header)
        self.contrast_label.place(relx=.78, rely=.85, anchor='c')

        # LEFT FRAME

        self.left_frame = Frame(self.frame, height=self.height,
                                bg=self.color_scheme.background_neutral,
                                highlightthickness=0)
        self.left_frame.place(relx=1, y=0, relwidth=.44, anchor='ne')

        file_info = Text(self.left_frame, height=6,
                         bg=self.color_scheme.background_neutral,
                         foreground=self.color_scheme.text,
                         borderwidth=0, wrap=WORD, spacing3=6, spacing2=4)
        file_info.tag_configure("bold", font='Helvetica 11 bold', justify='right',
                                foreground=self.color_scheme.text_header, spacing3=12)
        file_info.tag_configure("regular", font='Helvetica 11', justify='right')
        file_info.insert(END, "НАСТРОЙКА ЯРКОСТИ И КОНТРАСТА\n", 'bold')
        file_info.insert(END, self.model.video_filename, 'regular')
        file_info.insert(END, ", " + str(self.model.get_frames_count()) + " кадров", 'regular')
        file_info.insert(END, "\nНастройте яркость и контраст, чтобы начать обработку видео. "
                              "Частицы должны быть отчетливо видны на белом фоне для наилучшего "
                              "качества обработки ", 'regular')

        # Информация: название файла, кол-во кадров. Текст про то, что нужно делать

        file_info.place(relx=.95, rely=.1, relwidth=.95, anchor='ne')
        file_info.pack_propagate(0)

        self.btn = Button(self.left_frame, height=2, width=25,
                          text="Начать обработку",
                          cursor='hand2',
                          bg=self.color_scheme.background_dark,
                          fg=self.color_scheme.text_bright,
                          borderwidth=1,
                          font=('Helvetica', 12, 'bold'))
        self.btn.bind("<Button-1>", self.__start_preprocessing)
        self.btn.place(relx=.95, rely=.8, anchor='e')

        self.log.debug("Frame created")
        return self

    def __update_preview_canvas(self, b=None, c=None):
        if b is None:
            b = self.model.brightness
        if c is None:
            c = self.model.contrast
        self.log.debug('Update [%s, %s]', str(b), str(c))

        self.preview_image = self.__get_sample_image(b, c)
        self.preview_canvas.create_image(0, 0, anchor=NW, image=self.preview_image)

    def __get_sample_image(self, brightness, contrast):
        self.model.set_brightness_contrast(float(brightness), float(contrast))
        cv2_image = self.model.sample_frame_from_video(update=True)
        pil_image = Image.fromarray(cv2_image)
        pil_image = resize_keep_ratio(pil_image, 200)
        self.preview_canvas.config(width=pil_image.size[0])
        return ImageTk.PhotoImage(image=pil_image)

    def __start_preprocessing(self, event):
        if self.btn['state'] == DISABLED:
            return

        self.log.info("Starting brightness/contrast process")
        self.btn['state'] = DISABLED
        self.brightness_slider['state'] = DISABLED
        self.contrast_slider['state'] = DISABLED

        self.p_bar = ProgressBar(self.frame, 20, self.color_scheme)
        task = IterativeBackgroundTask(self.frame, self.model.start_contrast_process,
                                       self.p_bar.set_progress, self.__complete_preprocessing)
        task.start()

    def __complete_preprocessing(self):
        self.p_bar.finish()
        self.continue_callback()
