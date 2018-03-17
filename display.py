from numpy import zeros
import numpy
from PIL import BdfFontFile, Image
from rgbmatrix import graphics, RGBMatrixOptions, RGBMatrix

fp = open('6x10.bdf','rb')
b = BdfFontFile.BdfFontFile(fp)
fp.close()


def get_ascii_pixels(character, rotate=None):
    ascii_value = ord(character)

    im = b.glyph[ascii_value][3]
    pixels = list(im.getdata())
    width, height = im.size
    temp =  [pixels[i * width:(i + 1) * width] for i in range(height)]
    if character == 'i':
        slim = []
        for row in temp:
            slim.append(row[1:-1])
        temp = slim
    if rotate:
        #temp = numpy.flip(temp, 1)
        #temp = numpy.flipud(temp)
        #temp = numpy.flip(temp, 1)
        #temp = list(zip(*temp[::-1]))
        #temp = list(zip(*temp[::-1]))
        #temp = list(zip(*temp[::-1]))
        pass
    return temp


class Hardware(object):
    def __init__(self):
        self.options = RGBMatrixOptions()
        self.options.hardware_mapping = 'adafruit-hat'
        self.options.rows = 32
        self.options.parallel = 1
        self.options.chain_length = 4
        self.options.pwm_bits = 11
        self.options.brightness = 100
        self.options.pwm_lsb_nanoseconds = 130
        self.matrix = RGBMatrix(options = self.options)
        self.canvas = self.matrix.CreateFrameCanvas()
        self.default_color = graphics.Color(255,0,0)


class LineCursor(object):
    def __init__(self, canvas, line_number, get_letter=get_ascii_pixels, rotated=False, queue=None):
        self.canvas = canvas
        self.rotated = rotated
        self.line_number = line_number
        self.get_letter = get_letter
        self.pixels = []


        if self.rotated:
            self.start_column = 127
            self.stop_column = 64
            self.increment = -1
        else:
            self.start_column = 0
            self.increment = 1
            self.stop_column = 63


        self.current_column = self.start_column
        self.current_row = self.line_number
        self.current_text = None
        self.scroll_column = self.start_column

        self.queue_index = 0
        self.queue = []

    def get_next(self):
        #print self.queue
        if self.queue:
            self.queue_index += 1
            return self.queue[self.queue_index % len(self.queue)]
        else:
            return self.current_text

    def scroll(self):
        self.scroll_column += self.increment
        #print "Scroll Column: %s" % self.scroll_column
        if not self.valid_column(self.scroll_column):
            #print 'scroll resetting: (%s, %s)' % (self.current_column,
            #                                      self.current_row)
            self.current_column = self.start_column
            self.scroll_column = self.start_column
            self.current_text = self.get_next()
            #self.reset()
        self.current_row = self.line_number
        #else:
        #    self.current_column += 1
        #self.current_column = self.scroll_column
        self.clear()
        #if self.scroll_column == self.stop_column:
        #    self.reset()
        #    self.scroll_column = self.start_column


        self.draw_line(text=self.current_text, start_column=self.scroll_column, queue=self.queue,red=self.red, green=self.green, blue=self.blue)

    def reset(self):
        
        #self.current_row = 0
        #self.current_column = self.start_column
        #print 'calling reset'
        self.current_row = self.line_number
        self.current_column = self.start_column


    def clear(self):
        while self.pixels:
            (column, row) = self.pixels.pop()
            #print 'clearing: (%s, %s)' % (column, row)
            self.canvas.SetPixel(column, row, 0, 0, 0)


    def draw_line(self, text=None, queue=None, start_column=None,red=0, green=255, blue=0):
        self.red = red
        self.green = green
        self.blue = blue
        if text:
            self.current_text=text
        elif queue:
            self.queue = queue
            self.current_text = self.queue[self.queue_index]
        else:
            raise Exception("WTF?")
        if start_column:
            self.current_column = start_column
        #print self.current_column, self.current_row
        if not self.valid_column(self.current_column):
            #print 'Setting current column to: %s' % self.start_column
            self.current_column = self.start_column
        for letter in self.current_text:
            self.draw_letter(letter, red=red, green=green, blue=blue)

    def set_pixel(self, column, row, red=255, green=0, blue=0):
        self.canvas.SetPixel(column, row, red, green, blue)
        self.pixels.append((column, row))

    def valid_column(self, column):
        if self.rotated:
            return column > 63 and column < 128
        else:
            return column < 64

    def draw_letter(self, letter, red=255, green=255, blue=0):
        pixels = self.get_letter(letter)
        row_length = len(pixels)
        column_length = len(pixels[0])
        start_column = self.current_column

        for row in range(row_length):
            for column in range(column_length):
                if pixels[row][column]:
                    if self.valid_column(self.current_column):
                        self.set_pixel(self.current_column, self.current_row, red=red, green=green, blue=blue)
                    else:
                        pass
                self.current_column += self.increment
            self.current_column = start_column
            self.current_row += self.increment

        self.current_column += column_length * self.increment
        self.current_row = self.line_number


class ThreeLineDisplay(object):
    def __init__(self):
        self.hardware = Hardware()
        self.canvas = self.hardware.canvas
        self.forward_lines = []
        self.rotated_lines = []
        self.forward_lines.append(LineCursor(self.canvas,0 ))
        self.forward_lines.append(LineCursor(self.canvas, 10))
        self.forward_lines.append(LineCursor(self.canvas, 20))
        self.rotated_lines.append(LineCursor(self.canvas, 31, rotated=True))
        self.rotated_lines.append(LineCursor(self.canvas, 21, rotated=True))
        self.rotated_lines.append(LineCursor(self.canvas, 11, rotated=True))
        self.width = self.hardware.matrix.width
        self.height = self.hardware.matrix.height
        self.matrix = self.hardware.matrix
    def update(self):
        self.hardware.matrix.SwapOnVSync(self.canvas)

    def clear_line(self, line_number):
        self.forward_lines[line_number].clear()
        self.rotated_lines[line_number].clear()

    def reset_line(self, line_number):
        self.forward_lines[line_number].reset()
        self.rotated_lines[line_number].reset()
    def draw_the_line(self, line_number=None, text=None, queue=None, start_column=0, color = (255, 0, 0)):
        (red, green, blue) = color
        self.forward_lines[line_number].draw_line(text=text, start_column=start_column, queue=queue, red=red, green=green, blue=blue)
        self.rotated_lines[line_number].draw_line(text=text, start_column=127-start_column, queue=queue, red=red, green=green, blue=blue)

        #self.lines[line_number].draw_line(text, 0)
        #self.lines[line_number+3].draw_line(text, 0)

    def draw_image(self, image_path):
        image = Image.open(image_path)
        #image.thumbnail((self.height, self.width), Image.ANTIALIAS)
        image.resize((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
        self.matrix.SetImage(image, 0, 0)

    def scroll_line(self, line_number):
        self.forward_lines[line_number].scroll()
        self.rotated_lines[line_number].scroll()





