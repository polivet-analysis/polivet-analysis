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

import logging
from tkinter import *
from PIL import ImageTk
from PIL import Image as PilImage
from ui.color import ColorScheme
from ui.color import BrightColorScheme
from ui.color import DarkColorScheme
import ui.strips.title_strip
import ui.strips.load_video_strip
import ui.strips.locate_strip
import ui.strips.particle_choose_strip
import ui.strips.analytics_strip
import ui.strips.video_strip


class MainInterface:
    def __init__(self, model):
        self.log = logging.getLogger("MainInterface")
        self.model = model

        self.color_scheme = DarkColorScheme()

        self.root_frame = Tk()
        self.root_frame.title('Particle analysis')
        # self.root_frame.geometry('1024x576')
        self.root_frame.geometry('1024x1024')
        self.root_frame.configure(background=self.color_scheme.background_neutral)

        self.scroll_canvas = Canvas(self.root_frame, bg=self.color_scheme.background_neutral,
                                    borderwidth=0, highlightthickness=0)
        self.scroll_canvas.pack(side=LEFT, fill='both', expand=True)
        self.scroll_bar = Scrollbar(self.root_frame, command=self.scroll_canvas.yview)
        self.scroll_bar.pack(side=LEFT, fill='y', expand=False)
        self.scroll_canvas.configure(yscrollcommand=self.scroll_bar.set)

        self.__create_center_info_frame()

        self.main_container = Frame(self.scroll_canvas, bg=self.color_scheme.background_neutral,
                                    borderwidth=0, highlightthickness=0)
        self.main_container_tag = self.scroll_canvas.create_window((0, 0), window=self.main_container, anchor='nw')

        def on_configure(event):
            self.scroll_canvas.itemconfigure(self.main_container_tag, width=event.width)
            self.update_container_height()
        self.scroll_canvas.bind('<Configure>', on_configure)

        def on_mousewheel(event):
            self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.scroll_canvas.bind_all("<MouseWheel>", on_mousewheel)

        self.title_strip = ui.strips.title_strip.Strip(0, 240, self.color_scheme)
        self.title_strip.create_layer(self.main_container)
        self.title_strip.set_continue_callback(self.__open_video_load_frame)

        self.particle_choose_layer = None
        self.video_preview_layer = None
        self.analytics_frame = None

    def start(self):
        self.log.info("Starting main loop")
        self.root_frame.mainloop()

    def __create_center_info_frame(self):
        """ Frame with lemur and license text """
        self.info_frame = Canvas(self.scroll_canvas, bg=self.color_scheme.background_neutral,
                                 borderwidth=0, highlightthickness=0)
        self.info_frame.place(relx=.5, rely=.6, anchor='c', relwidth=1, height=400)

        lemur_image = PilImage.open('resources/misc/lemur.png')
        self.lemur_fun = ImageTk.PhotoImage(lemur_image)
        self.info_frame.create_image(512, 400 - 64, image=self.lemur_fun, anchor='s')

        self.description = Text(self.info_frame, height=3,
                                bg=self.color_scheme.background_neutral,
                                foreground=self.color_scheme.text,
                                highlightthickness=0,
                                borderwidth=0, wrap=WORD,
                                padx=10, pady=10)
        self.description.tag_configure("regular", font='Helvetica 9', justify='center')
        self.description.insert(END, "The program is distributed under the GNU GPL 3.0 License.\n"
                                     "Full text of the license available on\n"
                                     "https://github.com/polivet-analysis/polivet-analysis/blob/"
                                     "9af49d817de14313bee11d9b244e3c66ef73412a/LICENSE.TXT", "regular")
        self.description.configure(state='disabled')
        self.description.place(relx=.5, y=400, relwidth=.7, anchor='s')

    def __open_video_load_frame(self, filename):
        self.log.info("Opening video load frame '" + filename + "'")
        self.model.load_video_file(filename)
        self.video_load_frame = ui.strips.load_video_strip.Strip(240, 240,
                                                                 self.color_scheme,
                                                                 self.model)
        self.video_load_frame.set_continue_callback(self.__open_particle_location_layer)
        self.video_load_frame.create_layer(self.main_container)
        self.update_container_height()

    def __open_particle_location_layer(self):
        self.log.info("Opening particle location layer")
        self.model.create_tracker()
        self.locate_frame = ui.strips.locate_strip.Strip(480, 600,
                                                         self.color_scheme,
                                                         self.model)
        self.locate_frame.set_continue_callback(self.__open_particle_choose_layer)
        self.locate_frame.create_layer(self.main_container)
        self.main_container.config(bg=self.color_scheme.background_dark)
        self.update_container_height()
        self.scroll_canvas.yview_moveto('1.0')

    def __open_particle_choose_layer(self):
        self.log.info("Opening particle choose layer")
        if self.particle_choose_layer is not None:
            self.particle_choose_layer.detach()
            self.particle_choose_layer = None
        if self.video_preview_layer is not None:
            self.video_preview_layer.detach()
            self.video_preview_layer = None
        if self.analytics_frame is not None:
            self.analytics_frame.detach()
            self.analytics_frame = None

        self.particle_choose_layer = ui.strips.particle_choose_strip.Strip(1080, 400,
                                                                           self.color_scheme,
                                                                           self.model)
        self.particle_choose_layer.set_continue_callback(self.__open_video_preview_layer)
        self.particle_choose_layer.create_layer(self.main_container)
        self.update_container_height()
        self.scroll_canvas.yview_moveto('1.0')

    def __open_video_preview_layer(self):
        self.log.info("Opening video preview layer")
        if self.video_preview_layer is not None:
            self.video_preview_layer.detach()
            self.video_preview_layer = None

        self.model.create_analytics()
        self.video_preview_layer = ui.strips.video_strip.Strip(1480, 70,
                                                               self.color_scheme,
                                                               self.model)
        self.video_preview_layer.set_continue_callback(self.__open_analysis_layer)
        self.video_preview_layer.create_layer(self.main_container)
        self.update_container_height()

    def __open_analysis_layer(self):
        self.log.info("Opening analysis layer")
        if self.analytics_frame is not None:
            self.analytics_frame.detach()
            self.analytics_frame = None

        self.model.create_analytics()
        self.analytics_frame = ui.strips.analytics_strip.Strip(1600, 1550,
                                                               self.color_scheme,
                                                               self.model)
        self.analytics_frame.set_continue_callback(lambda: self.log.info("Program finished"))
        self.analytics_frame.create_layer(self.main_container)
        self.update_container_height()

    def update_container_height(self):
        height = 200  # blank offset
        for child in self.main_container.place_slaves():
            height += child.winfo_reqheight()
        self.scroll_canvas.itemconfigure(self.main_container_tag, height=height)
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox('all'))
