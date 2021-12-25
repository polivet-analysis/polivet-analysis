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
        self.log = logging.getLogger("TitleStrip")

    def set_continue_callback(self, callback):
        self.continue_callback = callback
        return self

    def create_layer(self, outer_frame):
        self.log.info("Creating frame")
        self.frame = Frame(master=outer_frame, height=self.height,
                           bg=self.color_scheme.background_dark)
        self.frame.place(x=0, y=self.y_position, relwidth=1)

        # PARAMETERS - LEFT SIDE

        self.parameters_frame = Frame(self.frame, height=self.height,
                                      bg=self.color_scheme.background_dark)
        self.parameters_frame.place(x=0, y=0, relwidth=.6, anchor='nw')

        header_height = 50
        self.header_frame = Frame(self.parameters_frame, height=header_height, bg=self.color_scheme.background_dark)
        self.header_frame.place(x=0, y=0, relwidth=1, anchor='nw')

        self.header_label = Label(self.header_frame, text='ПОИСК ЧАСТИЦ И ТРЕКИНГ',
                                  font=('Helvetica', 12, 'bold'),
                                  background=self.color_scheme.background_dark,
                                  foreground=self.color_scheme.text_bright)
        self.header_label.place(x=35, y=15, anchor='nw')

        self.parameters_values = Frame(self.parameters_frame, height=self.height - header_height,
                                       bg=self.color_scheme.background_dark)
        self.parameters_values.place(x=0, y=header_height, relwidth=.4, anchor='nw')

        self.diameter_label = Label(self.parameters_values, text='Диаметр',
                                    font=('Helvetica', 10, 'bold'),
                                    background=self.color_scheme.background_dark,
                                    foreground=self.color_scheme.text_bright)
        self.diameter_label.place(x=40, y=15, anchor='nw')

        self.diameter = IntVar(value=41)
        self.diameter_slider = Spinbox(self.parameters_values, from_=1, to=500,
                                       textvariable=self.diameter, width=10)
        self.diameter_slider.place(x=43, y=45, anchor='nw')

        self.minmass_label = Label(self.parameters_values, text='Минимальная масса',
                                   font=('Helvetica', 10, 'bold'),
                                   background=self.color_scheme.background_dark,
                                   foreground=self.color_scheme.text_bright)
        self.minmass_label.place(x=40, y=160, anchor='nw')

        self.minmass = IntVar(value=20)
        self.minmass_slider = Spinbox(self.parameters_values, from_=1, to=10000,
                                      textvariable=self.minmass, width=10)
        self.minmass_slider.place(x=42, y=190, anchor='nw')

        self.search_range_slider_label = Label(self.parameters_values, text='Скорость',
                                               font=('Helvetica', 10, 'bold'),
                                               background=self.color_scheme.background_dark,
                                               foreground=self.color_scheme.text_bright)
        self.search_range_slider_label.place(x=40, y=261, anchor='nw')

        self.search_range_slider_variable = IntVar()
        self.search_range_slider = Scale(self.parameters_values, from_=1, to=20, orient=HORIZONTAL,
                                         sliderrelief=FLAT, showvalue=0,
                                         variable=self.search_range_slider_variable,
                                         borderwidth=1, highlightthickness=0, cursor='hand2',
                                         foreground=self.color_scheme.text_bright,
                                         background=self.color_scheme.background_dark)
        self.search_range_slider.set(5)
        self.search_range_slider.place(x=43, y=290, anchor='nw')
        self.search_range_slider_show_value = Label(self.parameters_values,
                                                    foreground=self.color_scheme.text_bright,
                                                    background=self.color_scheme.background_dark,
                                                    textvariable=self.search_range_slider_variable)
        self.search_range_slider_show_value.place(x=150, y=290, anchor='nw')

        self.history_slider_label = Label(self.parameters_values, text='Связность',
                                          font=('Helvetica', 10, 'bold'),
                                          background=self.color_scheme.background_dark,
                                          foreground=self.color_scheme.text_bright)
        self.history_slider_label.place(x=40, y=380, anchor='nw')

        self.history_slider_variable = IntVar()
        self.history_slider = Scale(self.parameters_values, from_=1, to=20, orient=HORIZONTAL,
                                    sliderrelief=FLAT, showvalue=0,
                                    variable=self.history_slider_variable,
                                    borderwidth=1, highlightthickness=0, cursor='hand2',
                                    foreground=self.color_scheme.text_bright,
                                    background=self.color_scheme.background_dark)
        self.history_slider.set(5)
        self.history_slider.place(x=43, y=410, anchor='nw')
        self.history_slider_show_value = Label(self.parameters_values,
                                               foreground=self.color_scheme.text_bright,
                                               background=self.color_scheme.background_dark,
                                               textvariable=self.history_slider_variable)
        self.history_slider_show_value.place(x=150, y=409, anchor='nw')

        self.vertical_line = Canvas(self.parameters_values, width=2, height=470,
                                    highlightthickness=0,
                                    bg=self.color_scheme.accent)
        self.vertical_line.place(relx=1, y=18, anchor='n')

        self.parameters_description = Frame(self.parameters_frame, height=self.height - header_height,
                                            bg=self.color_scheme.background_dark)
        self.parameters_description.place(relx=.4, y=header_height, relwidth=.6, anchor='nw')

        self.diameter_description = Text(self.parameters_description, height=7,
                                         background=self.color_scheme.background_dark,
                                         foreground=self.color_scheme.text_bright,
                                         borderwidth=0, wrap=WORD, spacing3=8)
        self.diameter_description.tag_configure("regular", font='Helvetica 10')
        self.diameter_description.insert(END, "Минимальный диаметр частицы в пикселях. Если частица меньше этого "
                                              "размера, она не будет учитываться алгоритмом. В случае, если значение "
                                              "слишком мало, при линковке будет много коротких треков. Если же "
                                              "значение наоборот слишком велико, то количество частиц может быть "
                                              "недостатончо для сбора статистики.", 'regular')
        self.diameter_description.place(relx=.1, y=18, relwidth=.8, anchor='nw')

        self.minmass_description = Text(self.parameters_description, height=5,
                                        background=self.color_scheme.background_dark,
                                        foreground=self.color_scheme.text_bright,
                                        borderwidth=0, wrap=WORD, spacing3=8)
        self.minmass_description.tag_configure("regular", font='Helvetica 10')
        self.minmass_description.insert(END, "Минимальная суммарная яркость частицы. Чем выше параметр, тем больше "
                                             "рассеянных и едва различимых частиц будет отфильтровано. В конечную "
                                             "выборку будут попадать более четкие и яркие частицы.", 'regular')
        self.minmass_description.place(relx=.1, y=163, relwidth=.8, anchor='nw')

        self.search_range_description = Text(self.parameters_description, height=5,
                                             background=self.color_scheme.background_dark,
                                             foreground=self.color_scheme.text_bright,
                                             borderwidth=0, wrap=WORD, spacing3=8)
        self.search_range_description.tag_configure("regular", font='Helvetica 10')
        self.search_range_description.insert(END, "Максимальное расстояние, которое может пройти частица между двумя "
                                                  "кадрами. Чем быстрее частицы движутся в кадре, тем больше должен "
                                                  "быть параметр. При быстром движении частиц в кадре снижается "
                                                  "точность и ухудшается производительность.", 'regular')
        self.search_range_description.place(relx=.1, y=263, relwidth=.8, anchor='nw')

        self.history_description = Text(self.parameters_description, height=4,
                                        background=self.color_scheme.background_dark,
                                        foreground=self.color_scheme.text_bright,
                                        borderwidth=0, wrap=WORD, spacing3=8)
        self.history_description.tag_configure("regular", font='Helvetica 10')
        self.history_description.insert(END, "Количесество кадров, которые алгоритм использует для составления "
                                             "траектории частицы. Если частица пропадает на одном кадре и появляется "
                                             "на седующем в пределах заданного числа кадров, она будет привязана к "
                                             "той же траектории.", 'regular')
        self.history_description.place(relx=.1, y=382, relwidth=.8, anchor='nw')

        self.preview_frame = Frame(self.frame, bg=self.color_scheme.background_dark)
        self.preview_frame.place(relx=1, rely=0, relwidth=.4, relheight=.5, anchor='ne')

        self.preview_canvas = Canvas(self.preview_frame, height=200, width=350,
                                     highlightthickness=0)
        self.preview_canvas.place(relx=.9, rely=.95, anchor='se')

        self.control_frame = Frame(self.frame, bg=self.color_scheme.background_dark)
        self.control_frame.place(relx=1, rely=1, relwidth=.4, relheight=.5, anchor='se')

        self.update_button = Button(self.control_frame, width=20, height=2,
                                    bg=self.color_scheme.background_light,
                                    fg=self.color_scheme.text_header,
                                    disabledforeground=self.color_scheme.text_disabled,
                                    borderwidth=0, cursor='hand2',
                                    font=('Helvetica', 9, 'bold'),
                                    text="ОБНОВИТЬ")
        self.update_button.bind("<Button-1>", lambda e: self.__update_preview_canvas())
        self.update_button.place(relx=.9, rely=.05, anchor='ne')

        self.continue_button = Button(self.control_frame, width=20, height=2,
                                      bg=self.color_scheme.background_bright,
                                      fg=self.color_scheme.text_header,
                                      disabledforeground=self.color_scheme.text_disabled_bright,
                                      borderwidth=0, cursor='hand2',
                                      font=('Helvetica', 9, 'bold'),
                                      text="ТРЕКИНГ")
        self.continue_button.bind("<Button-1>", lambda e: self.__start_locate_process())
        self.continue_button.place(relx=.9, rely=.9, anchor='se')

        self.frame.after(100, self.__update_preview_canvas)

    def __update_preview_canvas(self):
        if self.update_button['state'] == DISABLED:
            return

        self.__loading_start()
        new_diameter = self.__check_diameter_value(self.diameter.get())
        self.model.set_diameter_minmass(new_diameter, self.minmass.get())

        self.preview = self.model.get_annotated_sample()
        self.preview = resize_keep_ratio(self.preview, 200)
        self.preview_canvas.config(width=self.preview.size[0])
        self.preview = ImageTk.PhotoImage(image=self.preview)
        self.preview_canvas.create_image(0, 0, anchor=NW, image=self.preview)
        self.__loading_finished()

    def __start_locate_process(self):
        if self.continue_button['state'] == DISABLED:
            return

        self.freeze_interface()

        self.p_bar = ProgressBar(self.frame, 20, self.color_scheme, dark=TRUE)
        self.p_bar.text_header = 'Поиск частиц'

        new_diameter = self.__check_diameter_value(self.diameter.get())
        self.model.set_diameter_minmass(new_diameter, self.minmass.get())

        task = IterativeBackgroundTask(self.frame, self.model.start_locate_process,
                                       self.p_bar.set_progress, self.__start_link_process)
        task.start()

    def __start_link_process(self):
        search_range = self.search_range_slider.get()
        memory = self.history_slider.get()
        self.model.set_range_memory(search_range, memory)

        self.p_bar.text_header = 'Линковка траекторий'

        task = IterativeBackgroundTask(self.frame, self.model.start_linkage_process,
                                       self.p_bar.set_progress, self.__finish_link_process)
        task.start()

    def __finish_link_process(self):
        self.p_bar.finish()
        self.continue_callback()
        self.unfreeze_interface()

    def __check_diameter_value(self, value):
        return value + 1 if value % 2 == 0 else value

    def __loading_start(self):
        self.preview_canvas.update_idletasks()

        def create_rectangle(x1, y1, x2, y2, **kwargs):
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = self.preview_canvas.winfo_rgb(fill) + (alpha,)
            image = PilImage.new('RGBA', (x2 - x1, y2 - y1), fill)
            self.loading_background = ImageTk.PhotoImage(image)
            self.loading_rectangle = self.preview_canvas.create_image(x1, y1,
                                                                      image=self.loading_background,
                                                                      anchor='nw')

        create_rectangle(0, 0, self.preview_canvas.winfo_width(), self.preview_canvas.winfo_height(),
                         fill=self.color_scheme.accent, alpha=.7, width=0)
        self.loading_txt = self.preview_canvas.create_text(self.preview_canvas.winfo_width() / 2,
                                                           self.preview_canvas.winfo_height() / 2,
                                                           fill=self.color_scheme.text,
                                                           anchor='n', font='Times 9', text='Загрузка')
        self.preview_canvas.update_idletasks()

    def __loading_finished(self):
        self.preview_canvas.delete(self.loading_rectangle)
        self.preview_canvas.delete(self.loading_txt)

    def freeze_interface(self):
        self.update_button['state'] = DISABLED
        self.continue_button['state'] = DISABLED
        self.diameter_slider['state'] = DISABLED
        self.minmass_slider['state'] = DISABLED
        self.history_slider['state'] = DISABLED
        self.search_range_slider['state'] = DISABLED

    def unfreeze_interface(self):
        self.update_button['state'] = NORMAL
        self.continue_button['state'] = NORMAL
        self.diameter_slider['state'] = NORMAL
        self.minmass_slider['state'] = NORMAL
        self.history_slider['state'] = NORMAL
        self.search_range_slider['state'] = NORMAL