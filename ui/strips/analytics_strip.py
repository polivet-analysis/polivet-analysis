#
#     Copyright (C) 2021  Tatiana Novosadjuk & Victoria Tsvetkova
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
from tkinter.filedialog import asksaveasfilename
from .image import resize_keep_ratio
from .thread import BackgroundCallableTask


class Strip:
    def __init__(self, y_position, height, color_scheme, model):
        self.y_position = y_position
        self.height = height
        self.color_scheme = color_scheme
        self.model = model
        self.continue_callback = None
        self.log = logging.getLogger("AnalyticsStrip")

    def set_continue_callback(self, callback):
        self.continue_callback = callback
        return self

    def create_layer(self, outer_frame):
        self.log.info("Creating frame")
        self.frame = Frame(master=outer_frame, height=self.height,
                           bg=self.color_scheme.background_dark)
        self.frame.place(x=0, y=self.y_position, relwidth=1)

        self.__create_header()

        self.fullTrajectories = FullTrajectoriesWidget(self.frame, 50, 300, self.model, self.color_scheme)
        self.singleTrajectory = SingleTrajectoryWidget(self.frame, 350, 300, self.model, self.color_scheme)
        self.msd = MSDWidget(self.frame, 650, 300, self.model, self.color_scheme)
        self.x_displacement = XDisplacementWidget(self.frame, 950, 300, self.model, self.color_scheme)
        self.y_displacement = YDisplacementWidget(self.frame, 1250, 300, self.model, self.color_scheme)

    def __create_header(self):
        self.header = Frame(self.frame, height=50, bg=self.color_scheme.background_dark)
        self.header.place(x=0, y=0, relwidth=1, anchor='nw')

        self.header_label = Label(self.header, text='ГРАФИКИ И АНАЛИТИКА',
                                  font=('Helvetica', 12, 'bold'),
                                  background=self.color_scheme.background_dark,
                                  foreground=self.color_scheme.text_bright)

        self.header_label.place(x=35, y=15, anchor='nw')

        horizontal_line = Canvas(self.header, width=260, height=2,
                                 bg=self.color_scheme.accent,
                                 borderwidth=0, highlightthickness=0)
        horizontal_line.place(x=0, y=40, anchor='nw')

    def detach(self):
        self.frame.place_forget()
        self.frame.destroy()


class StatWidget:
    def __init__(self, container, y_position, height, model, color_scheme):
        self.height = height
        self.model = model
        self.color_scheme = color_scheme
        self.margin = 50
        self.frame = Frame(container, height=self.height, bg=self.color_scheme.background_dark)
        self.frame.place(x=0, y=y_position, relwidth=1)

        self.right_frame = Frame(self.frame, height=self.height, bg=self.color_scheme.background_dark)
        self.right_frame.place(relx=1, y=0, relwidth=.5, anchor='ne')

        self.header = Label(self.right_frame, text="Header", font=('Helvetica', 12, 'bold'),
                            background=self.color_scheme.background_dark,
                            foreground=self.color_scheme.text_bright)
        self.header.place(relx=.05, rely=.2, anchor='nw')

        self.text = Text(self.right_frame, height=6,
                         background=self.color_scheme.background_dark,
                         foreground=self.color_scheme.text_bright,
                         borderwidth=0, wrap=WORD, spacing2=6)
        self.text.tag_configure("regular", font='Helvetica 10')
        self.text.insert(END, "Sample text, sample text, Sample text, sample text", "regular")
        self.text.place(relx=.05, rely=.35, relwidth=.8, anchor='nw')

        self.save_button = Button(self.right_frame, width=20, height=2,
                                  bg=self.color_scheme.background_light,
                                  fg=self.color_scheme.text_header,
                                  disabledforeground=self.color_scheme.text_disabled,
                                  borderwidth=0, cursor='hand2',
                                  font=('Helvetica', 9, 'bold'),
                                  text='СОХРАНИТЬ',
                                  command=self.save_image)
        self.save_button.place(relx=.05, rely=0.9, anchor='sw')

        self.left_frame = Frame(self.frame, height=self.height, bg=self.color_scheme.background_dark)
        self.left_frame.place(x=0, y=0, relwidth=.5, anchor='nw')

        cw, ch = self.__get_canvas_default_size()
        self.image_canvas = Canvas(self.left_frame, width=cw, height=ch)
        self.image_canvas.place(relx=0.95, rely=0.1, anchor='ne')

    def set_header(self, header):
        self.header.config(text=header)

    def set_text(self, text):
        self.text.delete('1.0', END)
        self.text.insert(END, text, 'regular')
        self.text['state'] = DISABLED

    def set_image(self, image):
        self.pil_image = image
        resized = resize_keep_ratio(image, self.height - self.margin)
        self.image_canvas.config(width=resized.size[0], height=resized.size[1])
        self.image = ImageTk.PhotoImage(resized)
        self.image_canvas.create_image(0, 0, anchor=NW, image=self.image)

    def load_image(self, image_provider):
        cw, ch = self.__get_canvas_default_size()
        self.image_canvas_load_text = self.image_canvas.create_text(cw / 2, ch / 2,
                                                                    fill=self.color_scheme.text_header,
                                                                    anchor='c', font=('Helvetica', 12, 'bold'),
                                                                    text='ЗАГРУЗКА')

        def set_loaded_image(image):
            self.set_image(image)
            self.image_canvas.delete(self.image_canvas_load_text)

        task = BackgroundCallableTask(self.frame, image_provider, on_complete=set_loaded_image)
        task.start()

    def save_image(self):
        filename = asksaveasfilename(filetypes=[('PNG image', '.png')], defaultextension='.png')
        if filename:
            self.pil_image.save(filename, 'PNG')

    def __get_canvas_default_size(self):
        return 16 * (self.height - self.margin) / 9, self.height - self.margin


class FullTrajectoriesWidget(StatWidget):
    def __init__(self, container, y_position, height, model, color_scheme):
        super().__init__(container, y_position, height, model, color_scheme)
        super().set_header("ТРАЕКТОРИИ ДВИЖЕНИЯ ЧАСТИЦ")
        super().set_text("Траектории движения частиц на всём временном отрезке. Каждая частица выделена своим "
                         "цветом. На этом графике можно наблюдать общее движение частиц.")

        super().load_image(model.get_analytics().get_all_trajectories_fig)


class SingleTrajectoryWidget(StatWidget):
    def __init__(self, container, y_position, height, model, color_scheme):
        super().__init__(container, y_position, height, model, color_scheme)
        super().set_header("ТРАЕКТОРИЯ ЧАСТИЦЫ")
        super().set_text("Траектория одной частицы, которая была выбрана выше. Оранжевой линией на графике показана "
                         "линейная аппроксимация траектории. В небольшом графике слева представлена гистограмма "
                         "среднеквадратичных смещений.")

        super().load_image(model.get_analytics().get_trajectory_stat_fig)


class MSDWidget(StatWidget):
    def __init__(self, container, y_position, height, model, color_scheme):
        super().__init__(container, y_position, height, model, color_scheme)
        super().set_header("СРЕДНЕКВАДРАТИЧНЫЕ СМЕЩЕНИЯ ЧАСТИЦ")
        super().set_text("Каждая линия на графике прдставляет собой частицу. По оси ординат отложены "
                         "среднеквадратичные смещения относительно начальной точки частицы. "
                         "По оси абсцисс отложено время в кадрах. Масштаб логарифмический.")

        super().load_image(model.get_analytics().get_msd_for_particles_fig)


class XDisplacementWidget(StatWidget):
    def __init__(self, container, y_position, height, model, color_scheme):
        super().__init__(container, y_position, height, model, color_scheme)
        super().set_header("СМЕЩЕНИЯ ПО ОСИ X")
        super().set_text("Гистограмма линейных смещений по оси абсцисс. Чем больше отклонения среднего значения "
                         "от нуля, тем быстрее движется поток частиц в направлении оси X.")

        super().load_image(model.get_analytics().get_x_displacement_fig)


class YDisplacementWidget(StatWidget):
    def __init__(self, container, y_position, height, model, color_scheme):
        super().__init__(container, y_position, height, model, color_scheme)
        super().set_header("СМЕЩЕНИЯ ПО ОСИ Y")
        super().set_text("Гистограмма линейных смещений по оси абсцисс. Чем больше отклонения среднего значения "
                         "от нуля, тем быстрее движется поток частиц в направлении оси Y.")

        super().load_image(model.get_analytics().get_y_displacement_fig)
