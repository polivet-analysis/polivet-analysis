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

import tkinter


class ProgressBar:
    def __init__(self, frame, height, color_scheme, dark=False):
        self.frame = frame
        self.height = height
        self.color_scheme = color_scheme
        self.text_header = 'Обработка'
        self.finished = False

        self.canvas = tkinter.Canvas(self.frame, height=self.height, bd=0, highlightthickness=0,
                                     bg=self.color_scheme.background_neutral)
        if dark:
            self.canvas.config(bg=self.color_scheme.background_dark)

        self.bar = self.canvas.create_rectangle(0, 18, 0, 20, fill=self.color_scheme.accent, width=0)
        self.canvas.place(rely=1, relx=0, relwidth=1, anchor='sw')
        self.canvas.update_idletasks()

        self.maxwidth = self.canvas.winfo_width()
        text_color = self.color_scheme.text if not dark else self.color_scheme.text_bright
        self.text = self.canvas.create_text(self.maxwidth / 2, 0,
                                            fill=text_color,
                                            anchor='n', font='Times 9',
                                            text=self.text_header + ' 0%')

        self.canvas.bind('<Configure>', lambda e: self.update_layout(e.width))

    def restart(self):
        self.finished = False

    def update_layout(self, width):
        self.canvas.coords(self.text, width / 2, 0)
        self.maxwidth = width
        if self.finished:
            x0, y0, x1, y1 = self.canvas.coords(self.bar)
            x1 = width
            self.canvas.coords(self.bar, x0, y0, x1, y1)

    def set_progress(self, index, total):
        x0, y0, x1, y1 = self.canvas.coords(self.bar)
        x1 = self.maxwidth * index / total
        self.canvas.coords(self.bar, x0, y0, x1, y1)
        self.canvas.itemconfigure(self.text, text=self.text_header + ' ' + str(round(index * 100 / total)) + '%')
        self.canvas.update_idletasks()

    def finish(self):
        self.finished = True
        self.update_layout(self.canvas.winfo_width())
        self.canvas.itemconfigure(self.text, text='Готово')
