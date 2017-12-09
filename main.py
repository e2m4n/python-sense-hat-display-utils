#!/usr/bin/env python
import sys
import argparse
from distutils.util import strtobool  # This is to fix argparse's lame boolean handling

from utility import SenseHatUtility, Colour


def main():
    available_actions = [i for i in SenseHatUtility.__dict__ if i[:1] != "_" and i == i.lower()]
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Sense HAT Utilities",
        epilog="(C) 2017 Aaron Fleming"
    )
    parser.add_argument("action", default="scroll", help="Currently implemented: {0}".format(available_actions))
    # Optional arguments with defaults
    parser.add_argument("--autorestore", type=strtobool, default=True, choices=[True, False], help="Restore the previous display when done")
    parser.add_argument("--colour", "--color", type=Colour, default="white", help="Output colour")
    parser.add_argument("--background_colour", "--background_color", type=Colour, default="black",
                        help="Output background colour")
    parser.add_argument("--invert", type=strtobool, default=False, help="Invert colours")
    parser.add_argument("--font", default=SenseHatUtility.DEFAULT_FONT,
                        help="Full path to font used for displaying text")
    parser.add_argument("--font_size", type=int, default=SenseHatUtility.DEFAULT_FONT_SIZE,
                        help="Point size to use for TrueType fonts")
    parser.add_argument("--font_y_offset", type=int, default=SenseHatUtility.DEFAULT_Y_OFFSET,
                        help="Offset text display up (negative values) or down (positive values)")
    parser.add_argument("--rotation", type=int, choices=[0, 90, 180, 270], default=180,
                        help="Set the rotation of the screen")
    parser.add_argument("--speed", type=float, default=0.05,
                        help="The number of seconds each frame is held when animating")
    parser.add_argument("--count", type=int, default=2, help="The number of times to repeat an action (if applicable)")
    # Optional arguments without defaults
    parser.add_argument("--message", help="Display this message instead of reading from stdin")
    parser.add_argument("--name", help="Some actions require a name to be passed")
    args = parser.parse_args()

    # Set any settings, then delete them from args, so that they're not passed to SHUtility as **kwargs
    shu = SenseHatUtility(args.autorestore)
    del args.autorestore

    shu.set_rotation(args.rotation)
    del args.rotation

    if args.action == "scroll1":
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
                getattr(shu, action)(**args.__dict__)
            except TypeError as ex:
                sys.exit("Error calling action '{0}': {1}".format(action, ex))
        else:
            sys.exit("Unknown action: {0} ".format(args.action))


if __name__ == "__main__":
    main()
