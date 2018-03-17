# PiProtest

![N|Solid](https://s-media-cache-ak0.pinimg.com/736x/74/3d/b5/743db576cd482fae244b3f4a91f03038.jpg)

PiProtest is a RaspberryPi based LCD protest sign that you can customize!
This is the first cut, so for now here's what we can do together!
  - Write up to three lines of text in any color.
  - Scroll the text.
  - Write a list of strings to each line that will change after each scroll.

# Installation
This project uses the awesome rpi-rgb-led-matrix library, so first thing, let's clone it (and our repo) and install the libraries.
```sh
sudo mkdir /protest
cd /protest
sudo git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
sudo git clone https://github.com/rghassemi/protest.git
cd rpi-rgb-led-matrix
sudo make -C examples-api-use
```
To test whether your hardware is working, run:
```sh
sudo examples-api-use/demo -D0 --led-gpio-mapping=adafruit-hat -c 2
```
Now let's finish the software installation
```sh
sudo apt-get update && sudo apt-get install python2.7-dev python-pillow -y
sudo make build-python
sudo make install-python
```

Sweet!  We're up and running!  Let's run the example code.
```sh
sudo python /protest/protest/example.py
```

### Hardware

We'll be updating this with more information soon.  For now, here's a link to the hardware.

| Hardware | Link |
| ------ | ------ |
| RaspberryPi 2 Model B | <todo> |
| Adafruit RGB Hat | https://www.adafruit.com/product/2345 |
| Type M DC Plug | <todo>  |
| Ribbon cable | <todo>  |
| Battery Pack | <todo>  |
| RGB LED Panels | https://www.adafruit.com/product/2277  |
