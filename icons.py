import time

W = [255, 255, 255]  # white
R = [255, 0, 0]  # red
G = [0, 255, 0]  # green
B = [0, 0, 255]  # blue
C = [0, 255, 255]  # cyan
M = [255, 0, 255]  # magenta
Y = [255, 255, 0]  # yellow
K = [0, 0, 0]  # black
O = [255, 128, 0]  # orange
P = [255, 0, 127]  # pink
L = [128, 255, 0]  # lime
T = [0, 255, 128]  # turquoise
U = [0, 128, 255]  # ultramarine
V = [127, 0, 255]  # violet
S = [128, 128, 128]  # stone


class SenseHatIcon(object):
    """
    A representation of an 8x8 icon for the Sense HAT display

    How shall we represent [R,G,B] * 8 * 8 ?
    Single character represents pixel colour?
    v1:

    W = [255, 255, 255]  # white
    R = [255, 0, 0]  # red
    G = [0, 255, 0]  # green
    B = [0, 0, 255]  # blue
    C = [0, 255, 255]  # cyan
    M = [255, 0, 255]  # magenta
    Y = [255, 255, 0]  # yellow
    K = [0, 0, 0]  # black

    v1.1 extended palette:
    O = [255, 128, 0]  # orange
    P = [255, 0, 127]  # pink
    L = [128, 255, 0]  # lime
    T = [0, 255, 128]  # turquoise
    U = [0, 128, 255]  # ultramarine
    V = [127, 0, 255]  # violet
    S = [128,128,128]  # stone

    """
    __sample = "\
    WRGBCMYK\
    WRGBCMYK\
    WRGBCMYK\
    WRGBCMYK\
    WRGBCMYK\
    WRGBCMYK\
    WRGBCMYK\
    WRGBCMYK\
    "

    def __init__(self, pixel_string=None):
        if pixel_string is None:
            self.pixels = [eval(i) for i in list(self.__sample.replace(" ", ""))]
        else:
            self.pixels = [eval(i) for i in list(pixel_string.replace(" ",
                                                                      ""))]  # This doesn't work now constants are "self.XXX" UPDATE: F**K YOU PYTHON
            # self.pixels = [eval(i) for i in list(["self."+item for item in list(pixel_string.replace(" ",""))])]


class SenseHatIconCollection(dict):
    """
    Icon collection for the Sense HAT
    """
    icons = {
        "template": "\
        BBBBBBBB\
        BBBBBBBB\
        BBBBBBBB\
        BBBBBBBB\
        BBBBBBBB\
        BBBBBBBB\
        BBBBBBBB\
        BBBBBBBB\
        ",
        "estelada": "\
        BYYYYYYY\
        BBRRRRRR\
        BBBYYYYY\
        BWBBRRRR\
        BBBYYYYY\
        BBRRRRRR\
        BYYYYYYY\
        KKKKKKKK\
        ",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for icon in self.icons:
            self[icon] = SenseHatIcon(self.icons[icon])

    def clock(self, hhmm=None):
        """
        Small analogue clock. Not very accurate.
        Can show eight hours, so have intervals of 12 / 8 = 1.5 hours
        Shift by 1.5 / 2 = 0.75 hours to shift to closest hour
        How many minutes? Minimum 8: 0,7.5,15,22.5,30,37.5,45,52.5
        Possibly try 16 by shifting outer segment one block clockwise, giving:
        0.0, 3.75, 7.5, 11.25, 15.0, 18.75, 22.5, 26.25, 30.0, 33.75, 37.5, 41.25, 45.0, 48.75, 52.5, 56.25, 60.0
        Returns:

        """
        template = "\
            RRRRRRRK\
            RKKKKKRK\
            RKKKKKRK\
            RKKRKKRK\
            RKKKKKRK\
            RKKKKKRK\
            RRRRRRRK\
            KKKKKKKK\
        ".replace(" ", "")

        if hhmm is None:
            now = time.localtime()
        else:
            now = time.strptime(hhmm,"%H%M")

        hours = now.tm_hour % 12
        minutes = now.tm_min
        decimal_time = hours + (minutes / 60)

        # Hours
        # if 0.0 <= decimal_time <= shift:  # 0.75
        #     template[19] = "W"
        # elif shift <= decimal_time <= (shift + interval):  # 2.25
        #     template[20] = "W"
        # elif (shift + interval) <= decimal_time <= (shift + (interval * 2)):  # 3.75
        #     template[28] = "W"
        # elif (shift + (interval * 2)) <= decimal_time <= (shift + (interval * 3)):  # 5.25
        #     template[36] = "W"
        # elif (shift + (interval * 3)) <= decimal_time <= (shift + (interval * 4)):  # 6.75
        #     template[35] = "W"
        # elif (shift + (interval * 4)) <= decimal_time <= (shift + (interval * 5)):  # 8.25
        #     template[34] = "W"
        # elif (shift + (interval * 5)) <= decimal_time <= (shift + (interval * 6)):  # 9.75
        #     template[26] = "W"
        # elif (shift + (interval * 6)) <= decimal_time <= (shift + (interval * 7)):  # 11.25
        #     template[18] = "W"
        # elif (shift + (interval * 7)) <= decimal_time <= (shift + (interval * 8)):  # 12.75
        #     template[19] = "W"

        # Hours
        interval = 12 / 8  # hours in clock face divided by hours able to display
        shift = interval / 2
        hour_map = {-1: 19, 0: 20, 1: 28, 2: 36, 3: 35, 4: 34, 5: 26, 6: 18, 7: 19}
        template = self._map_time_to_pixels(decimal_time, hour_map, interval, shift, template, 8)

        # Minutes
        interval = 60 / 16  # minutes in hour divided by minutes able to display
        shift = interval / 2
        minute_map = {
            -1: [19, 11], 0: [19, 12], 1: [20, 13], 2: [28, 21], 3: [28, 29], 4: [28, 37],
            5: [36, 45], 6: [35, 44], 7: [35, 43], 8: [35, 42], 9: [34, 41], 10: [26, 33],
            11: [26, 25], 12: [26, 17], 13: [18, 9], 14: [19, 10], 15: [19, 11]
        }
        template = self._map_time_to_pixels(minutes, minute_map, interval, shift, template, 16)

        return SenseHatIcon(template)

    @staticmethod
    def _map_time_to_pixels(decimal_time, pixel_map, interval, shift, template, stop, colour="W"):
        string_list = list(template)
        for i in range(-1, stop):
            if (shift + (interval * i)) <= decimal_time <= (shift + (interval * (i + 1))):
                if type(pixel_map[i]) is list:
                    for pixel in pixel_map[i]:
                        string_list[pixel] = colour
                else:
                    string_list[pixel_map[i]] = colour
                break
        return "".join(string_list)


if __name__ == '__main__':
    import doctest
    doctest.testmod()