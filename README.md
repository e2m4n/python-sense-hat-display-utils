# Raspberry Pi Sense HAT display utility library

Fun toys for the Sense HAT LED display. Works well with Home Assistant.

This code is not yet ready for public consumption, but it shouldn't do any damage.

## Currently implemented

### `print`

Print some text set with `--message` on the tiny 8x8 pixel display.

Not much good on its own, but is called by the next command.

### `scroll`

A classic scrolling text effect. Reads from stdin by default. Use the `--message` option to pass text from the command-line instead.

The default font has lots of accented characters, but you can use a different font with the `--font` option.
Both .ttf and .pil fonts are supported.

If you use a TrueType font then you might need to play with the `--font_size` option to make it readable.

Invert the display with `--invert true` or set foreground and background colours with `-c` and `-bg`. These can be named or "#rrggbb" hex colours.

Use `--repeat -1` to scroll forever.
Use `--autorestore true` to restore whatever was on the screen before when done scrolling.

### `pulse`

Pulse a colour (`-c`) out and in. Best used with the `--speed` and `--repeat` options.

### `show_clock`

Show a tiny analogue clock.

Use `--repeat -1` to use your Sense HAT as an inaccurate timekeeper.

### `fade_out`

Fade to black. Or, rather, fade to 47, which is the same thing.

### `show_icon`

Icons coming soon.


## Getting started

You'll need a Raspberry Pi and Sense HAT first.

### Prerequisites

Change to the directory you downloaded this to.

Install requirements:
```
pip install -r requirements.txt
```

### Running

Make sure it's all working:
```
python main.py scroll --message "Hello from the Raspberry Pi Sense HAT utility library!"
```

You should see the message scroll across your Sense HAT LEDs.

If it's upside down, then use the `--rotation` option (it's set to 180 by default).

## Using with Home Assistant

This works rather nicely combined with Home Assistant's notify module using its command-line platform.

### Prerequisites

Prepare Home Assistant:

* Add a new line to the end of `configuration.yaml`:
```
echo 'notify: !include notify.yaml' >> configuration.yaml
```

* Create `notify.yaml` and set up various notification entities:
```
- name: good
  platform: command_line
  command: /srv/homeassistant/bin/python /home/homeassistant/SenseHatUtilities/main.py -c green scroll
- name: bad
  platform: command_line
  command: /srv/homeassistant/bin/python /home/homeassistant/SenseHatUtilities/main.py -c red scroll
- name: warning
  platform: command_line
  command: /srv/homeassistant/bin/python /home/homeassistant/SenseHatUtilities/main.py -c yellow scroll
- name: info
  platform: command_line
  command: /srv/homeassistant/bin/python /home/homeassistant/SenseHatUtilities/main.py -c cyan scroll
```

* Restart Home Assistant

### Test it

* Go to Services, under Developer Tools
* Select the `notify.good` service
* In the Service Data field, enter `{"message":"Home Assistant is talking to you via SenseHatUtilities!"}`
* Click the Call Service button and watch your Sense HAT.

### Use it in your automations

* Send the current temperature

### Go further

You can chain calls easily with a shell script.

Make sure important messages aren't missed: try using the `pulse` action to flash the LEDs a few times before using `scroll_repeat` to repeat the message a few times.


## Acknowledgements

* Pi and Sense HAT creators
* Home Assistant creators
* Miniwi font creator

[Sphinx HTML Docs](doc/_build/index.html)
