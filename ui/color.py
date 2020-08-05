
class ColorScheme:
    def __init__(self, background_color_light, background_color_mid,
                 background_color_dark, neutral_color, accent_color,
                 text_color):
        self.background_color_light = background_color_light
        self.background_color_mid = background_color_mid
        self.background_color_dark = background_color_dark
        self.neutral_color = neutral_color
        self.accent_color = accent_color
        self.text_color = text_color


class BrightColorScheme:
    def __init__(self):
        self.background_light = '#fff'
        self.background_neutral = '#f2f4fb'
        self.background_bright = '#ff9280'
        self.accent = '#ff2400'
        self.accent_dark = '#45315d'
        self.text = '#777'
        self.text_header = '#1b5667'
        self.text_bright = '#fff'


class DarkColorScheme:
    def __init__(self):
        self.background_light = '#fff'
        self.background_neutral = '#f6f6f6'
        self.background_bright = '#fc3c3c'
        self.background_dark = '#3c4648'
        self.accent = '#fc3c3c'
        #self.accent_dark = '#45315d'
        self.text = '#777'
        self.text_header = '#3c4648'
        self.text_disabled = '#ccc'
        self.text_disabled_bright = '#cc3131'
        #self.text_dark = '#'
        self.text_bright = '#eee'
