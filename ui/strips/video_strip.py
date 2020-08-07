import logging
from tkinter import *
from .progress_bar import ProgressBar
from tkinter.filedialog import asksaveasfilename
from .thread import IterativeBackgroundTask


class Strip:
    def __init__(self, y_position, height, color_scheme, model):
        self.y_position = y_position
        self.height = height
        self.color_scheme = color_scheme
        self.model = model
        self.continue_callback = None
        self.log = logging.getLogger("VideoStrip")

    def set_continue_callback(self, callback):
        self.continue_callback = callback
        return self

    def create_layer(self, outer_frame):
        self.log.info("Creating frame")
        self.frame = Frame(master=outer_frame, height=self.height,
                           bg=self.color_scheme.background_dark)
        self.frame.place(x=0, y=self.y_position, relwidth=1)

        self.button_frame = Frame(self.frame, height=self.height, bg=self.color_scheme.background_dark)
        self.button_frame.place(x=0, y=0, relwidth=.6)

        self.button_movement = Button(self.button_frame, width=30, height=2,
                                      bg=self.color_scheme.background_light,
                                      fg=self.color_scheme.text_header,
                                      disabledforeground=self.color_scheme.text_disabled,
                                      borderwidth=0, cursor='hand2',
                                      font=('Helvetica', 9, 'bold'),
                                      text="Сохранить видео движения")
        self.button_movement.bind("<Button-1>", lambda e: self.save_movement_video())
        self.button_movement.place(relx=.3, rely=.4, anchor='c')

        self.button_rotation = Button(self.button_frame, height=2, width=30,
                                      bg=self.color_scheme.background_light,
                                      fg=self.color_scheme.text_header,
                                      disabledforeground=self.color_scheme.text_disabled,
                                      borderwidth=0, cursor='hand2',
                                      font=('Helvetica', 9, 'bold'),
                                      text="Сохранить видео вращения")
        self.button_rotation.bind("<Button-1>", lambda e: self.save_rotation_video())
        self.button_rotation.place(relx=.7, rely=.4, anchor='c')

        self.p_bar = None

        self.frame.after(100, self.continue_callback)

    def detach(self):
        self.frame.place_forget()
        self.frame.destroy()

    def init_p_bar(self):
        if self.p_bar is None:
            self.p_bar = ProgressBar(self.frame, 20, self.color_scheme, dark=True)
        else:
            self.p_bar.restart()

    def save_movement_video(self):
        if self.button_movement['state'] == DISABLED: return

        filename = asksaveasfilename(filetypes=[('Video file', '*.mp4')], defaultextension="*.mp4")
        if filename is not None and filename:
            self.freeze()
            self.init_p_bar()

            def action(listener): self.model.start_save_movement_video_process(filename, listener)

            task = IterativeBackgroundTask(self.frame, action, self.p_bar.set_progress, self.finish_saving_process)
            task.start()

    def save_rotation_video(self):
        if self.button_rotation['state'] == DISABLED: return

        filename = asksaveasfilename(filetypes=[('Video file', '*.mp4')], defaultextension="*.mp4")
        if filename is not None and filename:
            self.freeze()
            self.init_p_bar()

            def action(listener): self.model.start_save_rotation_video_process(filename, listener)

            task = IterativeBackgroundTask(self.frame, action, self.p_bar.set_progress, self.finish_saving_process)
            task.start()

    def finish_saving_process(self):
        self.p_bar.finish()
        self.unfreeze()

    def freeze(self):
        self.button_movement['state'] = DISABLED
        self.button_rotation['state'] = DISABLED

    def unfreeze(self):
        self.button_movement['state'] = NORMAL
        self.button_rotation['state'] = NORMAL
