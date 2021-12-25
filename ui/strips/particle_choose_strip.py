#
#     Copyright (C) 2021  Tatiana Novosadiuk & Viktoriia Tsvetkova
#
#     This file is part of Polevet-SPb-2020.
#
#     Polevet-SPb-2020 is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Polevet-SPb-2020 is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Polevet-SPb-2020.  If not, see <https://www.gnu.org/licenses/>.
#

import logging
from PIL import ImageTk
from PIL import Image as PilImage
from tkinter import *
from .image import resize_keep_ratio


class Strip:
    def __init__(self, y_position, height, color_scheme, model):
        self.y_position = y_position
        self.height = height
        self.color_scheme = color_scheme
        self.model = model
        self.continue_callback = None

        self.image_height = 350

        self.log = logging.getLogger("ParticleChoose")

    def set_continue_callback(self, callback):
        self.continue_callback = callback
        return self

    def create_layer(self, outer_frame):
        self.log.info("Creating frame")
        self.frame = Frame(master=outer_frame, height=self.height,
                           bg=self.color_scheme.background_dark)
        self.frame.place(x=0, y=self.y_position, relwidth=1)

        self.right_frame = Frame(self.frame, height=self.height,
                                 bg=self.color_scheme.background_dark)
        self.right_frame.place(relx=1, y=0, relwidth=.4, anchor='ne')

        self.header_text = Label(self.right_frame, text='ВЫБОР ЧАСТИЦЫ ДЛЯ АНАЛИЗА',
                                 font=('Helvetica', 12, 'bold'),
                                 background=self.color_scheme.background_dark,
                                 foreground=self.color_scheme.text_bright)
        self.header_text.place(relx=.05, y=25)

        self.description = Text(self.right_frame, height=10,
                                background=self.color_scheme.background_dark,
                                foreground=self.color_scheme.text_bright,
                                borderwidth=0, wrap=WORD, spacing2=6)
        self.description.tag_configure('regular', font='Helvetica 11')
        self.description.insert(END, 'Нажмите левой кнопкой мыши на частицу, чтобы выбрать её для анализа. Для '
                                     'частицы будет показана траектория и характеристики. Выбирайте длинные '
                                     'траектории с большим количеством кадров, чтобы улучшить качество данных '
                                     'аналитики.', 'regular')
        self.description.place(relx=.05, y=70, relwidth=.9)

        self.track_length_label = Label(self.right_frame, text='Длина траектории: --',
                                        font=('Helvetica', 11),
                                        background=self.color_scheme.background_dark,
                                        foreground=self.color_scheme.text_bright)
        self.track_length_label.place(relx=.05, y=220)

        self.choose_preview_frame = Frame(self.frame, height=self.height,
                                          bg=self.color_scheme.background_dark)
        self.choose_preview_frame.place(x=0, y=0, relwidth=.6)

        img = self.model.get_annotated_sample_choose_particle(0, 0)
        resized = resize_keep_ratio(img, self.image_height)
        self.annotated_image = ImageTk.PhotoImage(resized)

        target_size = PilImage.fromarray(self.model.sample_frame_from_video()).size
        self.size_scale = SizeCoordsScale(target_size, resized.size)

        self.canvas = Canvas(self.choose_preview_frame,
                             width=resized.size[0],
                             height=resized.size[1],
                             bd=0, highlightthickness=0)
        self.canvas.place(relx=.5, rely=.5, anchor='c')
        self.canvas.create_image(0, 0, anchor=NW, image=self.annotated_image)

        self.continue_button = Button(self.right_frame, width=20, height=2,
                                      bg=self.color_scheme.background_light,
                                      fg=self.color_scheme.text_header,
                                      disabledforeground=self.color_scheme.text_disabled,
                                      borderwidth=0, cursor='hand2',
                                      font=('Helvetica', 9, 'bold'),
                                      text='АНАЛИТИКА',
                                      command=self.continue_callback)
        self.continue_button.place(relx=.05, rely=.9, anchor='sw')

        def on_canvas_click(event):
            tx, ty = self.size_scale.to_original(event.x, event.y)
            img = self.model.get_annotated_sample_choose_particle(tx, ty)
            resized = resize_keep_ratio(img, self.image_height)
            self.annotated_image = ImageTk.PhotoImage(resized)
            self.canvas.create_image(0, 0, anchor=NW, image=self.annotated_image)

            track_length = self.model.get_trajectory_length_of_chosen_particle()
            self.track_length_label.config(text='Длина траектории: ' + str(track_length))
        self.canvas.bind("<Button-1>", on_canvas_click)

    def detach(self):
        self.frame.place_forget()
        self.frame.destroy()


class SizeCoordsScale:
    def __init__(self, original, target):
        self.w_original, self.h_original = original
        self.w_target, self.h_target = target

    def to_original(self, tx, ty):
        ox = self.w_original * tx / self.w_target
        oy = self.h_original * ty / self.h_target
        return ox, oy
