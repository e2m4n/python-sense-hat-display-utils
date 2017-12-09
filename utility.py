import os
import sys
import time

from PIL import Image, ImageDraw, ImageFont
from colour import Color as _Color
from sense_hat import SenseHat

from icons import SenseHatIconCollection


class Colour(_Color):
    def __getattr__(self, item):
        """
        This function exists because colour.Color is too clever for its own good
         (actually, maybe I was being silly when I forgot to remove the reference - TODO: try removing this function)
        Args:
            item (str): name of attribute

        Returns:
            Reference to the attribute <item>

        """
        if item == "get_rgb_int":
            return self.get_rgb_int()
        else:
            return super(Colour, self).__getattr__(item)

    def __init__(self, color=None, **kwargs):
        """
        Is this necessary? Try removing it and seeing what happens!
        Args:
            color:
            **kwargs:
        """
        super().__init__(color, **kwargs)

    def get_rgb_int(self):
        """
        The only thing that the colour.Color library doesn't do!

        Returns: The colour in (0-255) range for PIL compatibility

        """
        return tuple([int(float_colour * 255) for float_colour in self.get_rgb()])


class SenseHatUtility(object):
    """
        This class wraps the SenseHat class to provide display-related functions
    """

    DEFAULT_SPEED = 0.1  # speed is passed to time.sleep() to hold a frame
    WIDTH = 8  # Maybe if a SenseHat v2 comes out one day?
    HEIGHT = 8
    ZERO_BRIGHTNESS = 47  # offset. 47 == 0 in terms of Sense HAT's brightness.
    DEFAULT_FONT = "fonts/miniwi-8.pil"  # https://github.com/josuah/miniwi
    DEFAULT_FONT_SIZE = 6  # Bigger font, bigger size. AKA letter 'width' in the scroll function
    DEFAULT_X_OFFSET = 0  # "Don't touch this" - MC Hammer
    DEFAULT_Y_OFFSET = 0  # Some TrueType fonts have a lot of padding (to make room for accents?) and setting this to +/- 1 can make them fit better
    DEFAULT_FOREGROUND = "white"  # The colour module supports colour names or web RGB notation (plus other ways of creating colours)
    DEFAULT_BACKGROUND = "black"

    def __init__(self, autorestore=True):
        """
        Initialise reference to SenseHat and take a copy of the current screen state.

        Args:
            autorestore (bool, optional): Restore initial screen state when destroyed. Defaults to True.
        """
        self.autorestore = autorestore
        self.sh = SenseHat()
        self._font = None
        self._fade_backup = None
        self._backup = None
        self.backup()

    def __del__(self):
        """
        Restore the original display when done

        """
        self.fade_out()
        if self.autorestore:
            self.restore()
        self.sh = None

    def __getattr__(self, item):
        """
        This passes any calls to functions which don't exist to the SenseHat library.

        Args:
            item (str): Function name.

        Returns:
            Reference to the function via getattr().

        Raises:
            AttributeError: if not found

        Examples:
            This won't get called directly

            >>> shu = SenseHatUtility()
            >>> shu.low_light = True

            >>> shu.low_light
            True
            >>> shu.__getattr__("qwertyuiop")
            Traceback (most recent call last):
              File "<input>", line 1, in <module>
              File "/home/osmc/SenseHatProject/utility.py", line 98, in __getattr__
                raise AttributeError()
            AttributeError

        """
        if hasattr(self.sh, item):
            return getattr(self.sh, item)
        else:
            raise AttributeError()

    def _set_font(self, font, font_size):
        """
        Load the font and set self._font, fallback to default if any issues
        Args:
            font: relative or absolute path to font file, TrueType or PIL format
            font_size: used for TrueType fonts

        Examples:
            >>> shu = SenseHatUtility()
            >>> shu._set_font(shu.DEFAULT_FONT, shu.DEFAULT_FONT_SIZE)

            >>> shu._get_font().file.split("/")[-1].split(".")[0] == shu.DEFAULT_FONT.split("/")[-1].split(".")[0]
            True

        """
        try:
            if os.path.isabs(font):
                full_font_path = font
            else:
                full_font_path = "{}{}{}".format(os.path.dirname(os.path.abspath(__file__)), os.sep, font)

            if font[-3:] == "ttf":
                self._font = ImageFont.truetype(full_font_path, font_size)
            elif font[-3:] == "pil":
                self._font = ImageFont.load(full_font_path)
        except Exception as ex:
            self._font = ImageFont.load_default()

    def _get_font(self):
        """
        Get _font stored by _set_font. Calls _set_font if _font not yet set.
        Returns:
            ImageFont object

        Examples:
            >>> shu = SenseHatUtility()
            >>> shu._get_font() #doctest: +ELLIPSIS
            <PIL.ImageFont.ImageFont object at 0x...>

            >>> shu._get_font().file.split("/")[-1].split(".")[0] == shu.DEFAULT_FONT.split("/")[-1].split(".")[0]
            True

        """
        if self._font is None:
            self._set_font(self.DEFAULT_FONT, self.DEFAULT_FONT_SIZE)
        return self._font

    def print(self,
              message,
              colour=Colour(DEFAULT_FOREGROUND),
              background_colour=Colour(DEFAULT_BACKGROUND),
              x=DEFAULT_X_OFFSET,
              y=DEFAULT_Y_OFFSET,
              invert=False,
              font=DEFAULT_FONT,
              font_size=DEFAULT_FONT_SIZE,
              **kwargs
              ):
        """
        Print message to the display.

        Args:
            message (str): The text to display (only 2, maybe 3 characters will be visible).
            colour: The colour to display in
            background_colour: The colour to display _on_
            font: The font (use something that's readable at around 8pt).
            font_size: For TrueType fonts. Defaults to 8.
            x: The x position to start drawing at. Use this when scrolling.
            y: The y position to start drawing at. Usually used to slightly reposition fonts.
            invert: Invert the colours (black text on <colour> background).

        Returns:

        """
        # Set the font if not already done
        if self._font is None and (font is not self.DEFAULT_FONT or font_size is not self.DEFAULT_FONT_SIZE):
            self._set_font(font, font_size)
        font = self._get_font()

        # The image to output
        image = Image.new("RGB", (self.WIDTH, self.HEIGHT),
                          colour.get_rgb_int() if invert else background_colour.get_rgb_int())

        # The drawing utility
        draw = ImageDraw.Draw(image)

        # Draw the text on the image. Calling strip() to avoid passing a multiline string to draw.text, which causes an exception with the default fallback font
        draw.text((x, y), message.strip(), background_colour.get_rgb_int() if invert else colour.get_rgb_int(), font)

        # Output the image to the Sense HAT
        self.sh.set_pixels(list(map(list, image.getdata())))

    def scroll(self,
               message,
               colour=Colour(DEFAULT_FOREGROUND),
               background_colour=Colour(DEFAULT_BACKGROUND),
               speed=DEFAULT_SPEED,
               font_y_offset=DEFAULT_Y_OFFSET,
               invert=False,
               font=DEFAULT_FONT,
               font_size=DEFAULT_FONT_SIZE,
               **kwargs
               ):
        if self._font is None:
            self._set_font(font, font_size)

        if message is None:
            # Then read from stdin instead
            for line in sys.stdin:
                self.scroll(line, colour, background_colour, speed, font_y_offset, invert)
        else:
            # Start off-screen (self.WIDTH), end at the approximate end of message ( -(length*size) ), stepping backwards (-1)
            for position in range(self.WIDTH, (-1 * len(message) * font_size), -1):
                self.print(message, colour, background_colour, position, font_y_offset, invert)
                time.sleep(speed)

    def scroll_repeat(self, count=2, **kwargs):
        for number in range(0, count):
            self.scroll(**kwargs)

    def show_icon(self, name, **kwargs):
        """
        Load an icon by name and show it.

        Args:
            name: Name of icon

        """
        icon = SenseHatIconCollection()
        self.sh.set_pixels(icon[name].pixels)

    def show_clock(self, **kwargs):
        """
        Load the dynamic clock and show it.

        Args:
            **kwargs: unused

        """
        icon = SenseHatIconCollection()
        self.sh.set_pixels(icon.clock().pixels)

    def show_clock_forever(self, **kwargs):
        """
        Show the clock until interrupted by CTRL+C

        Args:
            **kwargs: unused

        """
        while True:
            self.show_clock(**kwargs)
            time.sleep(30)

    def _xy2px(self, x, y):
        """
        Helper to transform XY coordinates in the -4 to +4 range into a pixel number

        Notes:

        00 01 02 03 04 05 06 07
        08 09 10 11 12 13 14 15
        16 17 18 19 20 21 22 23
        24 25 26 27 28 29 30 31
        32 33 34 35 36 37 38 39
        40 41 42 43 44 45 46 47
        48 49 50 51 52 53 54 55
        56 57 58 59 60 61 62 63

        What about this?
           -4 -3 -2 -1 +1 +2 +3 +4
        +4
        +3
        +2
        +1
        -1
        -2
        -3
        -4
        Easier to 'draw' on, but need to translate between the two...
        in: coordinate, eg -2,+2
        out: pixel, eg 18
        steps: re-root coordinate - add 4 to X and  subtract 4 from Y, then flip +/- (eg. +2,+2)
            multiply Y by 8 to get row start (eg. 16)
            add X to get pixel (eg. 18)

        Warnings:
            There is no zero! This may turn out to be a big problem. Hope not...
            Yep. So... after re-rooting coordinates, there's (obviously) a gap
            if resulting X is > 4 then subtract 1
            if resulting Y is > 4 then subtract 1
            should fix it... :-/

        Args:
            x: X coordinate (between -4 and +4)
            y: Y coordinate (between -4 and +4)

        Returns:
            pixel number (between 0 and 63)

        Examples:


            >>> shu = SenseHatUtility()
            >>> shu._xy2px(-2, 2)
            18
            >>> shu._xy2px(-4, 4)
            0
            >>> shu._xy2px(4, 4)
            7
            >>> shu._xy2px(4, -4)
            63
            >>> shu._xy2px(-4, -4)
            56
            >>> shu._xy2px(2,8) #doctest: +ELLIPSIS
            Traceback (most recent call last):
              File "<input>", line 1, in <module>
              File ".../utility.py", line ..., in _xy2px
                assert -4 <= y <= 4
            AssertionError
            >>> ([shu._xy2px(x,y) for x in range(-4,4) for y in range(-4,4) if x is not 0 and y is not 0 ])
            [56, 48, 40, 32, 24, 16, 8, 57, 49, 41, 33, 25, 17, 9, 58, 50, 42, 34, 26, 18, 10, 59, 51, 43, 35, 27, 19, 11, 60, 52, 44, 36, 28, 20, 12, 61, 53, 45, 37, 29, 21, 13, 62, 54, 46, 38, 30, 22, 14]



        """
        assert -4 <= x <= 4
        assert -4 <= y <= 4
        assert x != 0
        assert y != 0

        a, b = x + 4, -1 * (y - 4)
        a = a - 1 if a > 4 else a
        b = b - 1 if b > 4 else b
        p = a + (b * 8)
        return p

    def pulse(self, colour, speed, count, **kwargs):
        """
        Pulse a colour from 4 pixels lit in the middle to all-but-4 pixels lit.

        Args:
            colour:
            speed: value to time.sleep() for
            count: Number of repetitions
            **kwargs:

        Returns:

        """
        c = list(colour.get_rgb_int())
        # Old approach (didn't work, code looks horrible)
        # frames = 7 * [64 * [[0, 0, 0]]]
        #
        # for i in (27, 28, 35, 36):
        #     frames[0][i] = c
        #     frames[6][i] = c
        # for i in (26, 27, 28, 29, 34, 35, 36, 37, 19, 20, 43, 44):
        #     frames[1][i] = c
        #     frames[5][i] = c
        # for i in (11, 12, 18, 19, 20, 21, 25, 26, 27, 28, 29, 30, 33, 34, 35, 36, 37, 38, 42, 43, 44, 45, 51, 52):
        #     frames[2][i] = c
        #     frames[4][i] = c
        # for i in (
        #         3, 4, 10, 11, 12, 13, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37,
        #         38, 39, 41, 42, 43, 44, 45, 46, 50, 51, 52, 53, 59, 60):
        #     frames[3][i] = c

        # New approach
        # draw in one quadrant and copy it
        #
        count_reverse_at = int(self.WIDTH / 2)  # 4
        count_to = count * count_reverse_at * 2
        start = 1

        for i in range(start, count_to + 1):
            for j in range(start, count_reverse_at + 1):  # Grow
                frame = self._pulse_get_frame(c, j)
                self.sh.set_pixels(frame)
                time.sleep(speed)
            for j in range(count_reverse_at, start - 1, -1):  # Shrink
                frame = self._pulse_get_frame(c, j)
                self.sh.set_pixels(frame)
                time.sleep(speed)

    def _pulse_get_frame(self, colour, frame_number):
        """
        Calculates which pixels need to be on for a given frame
        Args:
            colour: The colour to light the pixels
            frame_number: The frame number to calculate pixels for

        Returns:
            frame (list)

        """
        frame = 64 * [[0, 0, 0]]
        # draw from x=-j to j
        for pix in range(-frame_number, frame_number + 1):
            if pix is not 0:
                if -4 < pix < 4:  # Don't set the outermost corner pixels
                    self._pulse_set_pixels(frame, pix, -pix, colour)
                # draw along x and y axes
                self._pulse_set_pixels(frame, 1, pix, colour)
                if pix < -2 or pix > 2:  # draw along x,y=2 axes
                    self._pulse_set_pixels(frame, 2, pix, colour)
        return frame

    def _pulse_set_pixels(self, frame, x, y, colour):
        """
        Sets a pixel and it's 4 mirrors (horizontally and vertically)
        Args:
            frame: The frame to work on
            x: The x coordinate of the initial pixel to set
            y: The y coordinate of the initial pixel to set
            colour: The colour to set the pixel

        Returns:
            Modifies frame list in-place

        """
        for a in [x, -x]:
            frame[self._xy2px(a, y)] = colour
            frame[self._xy2px(y, a)] = colour

    def fade_out(self, speed=DEFAULT_SPEED, **kwargs):
        """
        Fade out the display

        Args:
            speed: passed to time.sleep() in between fade steps

        Returns:

        """
        zb = self.ZERO_BRIGHTNESS
        steps = 256 - zb
        fade = self._fade_backup = self.sh.get_pixels()
        for i in range(0, steps):
            fade = [[max(0, r - 1), max(0, g - 1), max(0, b - 1)] for r, g, b in fade]
            self.sh.set_pixels(fade)
            # if all([x == [0,0,0] for x in fade]):  # If all pixels are black then exit
            if all([[r < zb, g < zb, b < zb] for i in fade for r, g, b in [i]]):
                break
            time.sleep(speed)

    def backup(self):
        self._backup = self.sh.get_pixels()

    def restore(self):
        self.sh.set_pixels(self._backup)


if __name__ == '__main__':
    import doctest

    doctest.testmod()
