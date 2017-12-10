#!/usr/bin/env python
import argparse
import sys
from distutils.util import strtobool  # This is to fix argparse's lame boolean handling

from sense_hat_display_utils.utility import SenseHatUtility, Colour


def main():
    available_actions = [i for i in SenseHatUtility.__dict__ if i[:1] != "_" and i == i.lower()]
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Sense HAT Utilities",
        epilog="(C) 2017 Aaron Fleming"
    )
    parser.add_argument("action", default="scroll", help="Currently implemented: {0}".format(available_actions))
    # Optional arguments with defaults
    parser.add_argument("-a", "--autorestore", type=strtobool, default=False, choices=[True, False],
                        help="Restore the previous display when done. Can be useful to set this to True when using the 'scroll' and 'pulse' actions")
    parser.add_argument("-c", "--colour", "--color", type=Colour, default="white", help="Output colour")
    parser.add_argument("-bg", "--background_colour", "--background_color", type=Colour, default="black",
                        help="Output background colour")
    parser.add_argument("-i", "--invert", type=strtobool, default=False,
                        help="Invert text foreground and background colours")
    parser.add_argument("-f", "--font", default=SenseHatUtility.DEFAULT_FONT,
                        help="Full path to font used for displaying text")
    parser.add_argument("--font_size", type=int, default=SenseHatUtility.DEFAULT_FONT_SIZE,
                        help="Point size to use for TrueType fonts")
    parser.add_argument("-y", "--font_y_offset", type=int, default=SenseHatUtility.DEFAULT_Y_OFFSET,
                        help="Offset text display up (negative values) or down (positive values)")
    parser.add_argument("--rotation", type=int, choices=[0, 90, 180, 270], default=180,
                        help="Set the rotation of the screen")
    parser.add_argument("-s", "--speed", type=float, default=0.05,
                        help="The number of seconds each frame is held when animating")
    parser.add_argument("-r", "--repeat", type=int, default=1,
                        help="The number of times to repeat an action. -1 = repeat until killed with CTRL+C")
    # Optional arguments without defaults
    parser.add_argument("-m", "--message", help="Display this message instead of reading from stdin")
    parser.add_argument("-n", "--name", help="Some actions require a name to be passed")
    args = parser.parse_args()

    # Set any settings, then delete them from args, so that they're not passed to SHUtility as **kwargs
    shu = SenseHatUtility(args.autorestore)
    del args.autorestore

    shu.set_rotation(args.rotation)
    del args.rotation

    if args.action == "example":
        # Specific function call:
        if hasattr(args, "message"):
            shu.scroll(args.message, args.colour, args.speed)
        else:
            for line in sys.stdin:
                shu.scroll(line, args.colour, args.speed)
    else:
        # Generic function call:
        if hasattr(shu, args.action):
            # Strip action from args - function won't be expecting them
            action = args.action
            del args.action
            try:
                if args.repeat is -1:
                    del args.repeat
                    while True:
                        getattr(shu, action)(**args.__dict__)
                else:
                    getattr(shu, action)(**args.__dict__)
            except TypeError as ex:
                sys.exit("Error calling action '{0}': {1}".format(action, ex))
        else:
            sys.exit("Unknown action: {0} ".format(args.action))


if __name__ == "__main__":
    main()
