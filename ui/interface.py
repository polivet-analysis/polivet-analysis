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
        #self.root_frame.geometry('1024x576')
        self.root_frame.geometry('1024x1024')
        self.root_frame.configure(background=self.color_scheme.background_neutral)

        self.scroll_canvas = Canvas(self.root_frame, bg=self.color_scheme.background_neutral)
        self.scroll_canvas.pack(side=LEFT, fill='both', expand=True)
        self.scroll_bar = Scrollbar(self.root_frame, command=self.scroll_canvas.yview)
        self.scroll_bar.pack(side=LEFT, fill='y', expand=False)
        self.scroll_canvas.configure(yscrollcommand=self.scroll_bar.set)

        lemur_image = PilImage.open('resources/misc/lemur.png')
        self.lemur_fun = ImageTk.PhotoImage(lemur_image)
        self.scroll_canvas.create_image(1024 / 2,
                                        1024 / 2,
                                        image=self.lemur_fun, anchor='c')

        self.main_container = Frame(self.scroll_canvas, bg=self.color_scheme.background_neutral)
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

        self.video_preview_layer = None
        self.analytics_frame = None

    def start(self):
        self.log.info("Starting main loop")
        self.root_frame.mainloop()

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
