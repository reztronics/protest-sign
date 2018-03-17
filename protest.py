from numpy import zeros
import pika
import numpy
from PIL import BdfFontFile
from rgbmatrix import graphics, RGBMatrixOptions, RGBMatrix
import time

fp = open('/protest/protest/6x10.bdf','rb')
b = BdfFontFile.BdfFontFile(fp)
fp.close()

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
channel.basic_qos(prefetch_count=1)
the_text = "Life"
def suscriber(ch,method , properties , body):
        print "[Y] received %r " % (body,)
        time.sleep( body.count('.') )
        print " [x] Done"
        the_text = body
        ch.basic_ack(delivery_tag = method.delivery_tag)

#channel.basic_consume(suscriber, queue = 'task_queue' )

def get_ascii_pixels(character, rotate=None):
    ascii_value = ord(character)

    im = b.glyph[ascii_value][3]
    pixels = list(im.getdata())
    width, height = im.size
    temp =  [pixels[i * width:(i + 1) * width] for i in range(height)]
    if rotate:
        #temp = numpy.flip(temp, 1)
        #temp = numpy.flipud(temp)
        #temp = numpy.flip(temp, 1)
        #temp = list(zip(*temp[::-1]))
        #temp = list(zip(*temp[::-1]))
        #temp = list(zip(*temp[::-1]))
        pass
    return temp


def print_letter(letter):
    for row in letter:
        temp = ''
        for char in row:
            temp += '*' if char else ' '
        print(temp)


class Cocktapus(object):
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
    def __init__(self, canvas, line_number, get_letter=get_ascii_pixels, rotated=False):
        self.canvas = canvas
        self.rotated = rotated
        self.line_number = line_number
        self.get_letter = get_letter

        if self.rotated:
            self.start_column = 127
            self.increment = -1
        else:
            self.start_column = 0
            self.increment = 1
        self.current_column = self.start_column
        self.current_row = self.line_number

    def reset(self):
        
        self.current_row = 0
        self.current_column = self.start_column

    def draw_line(self, text, start_column=None):
        if start_column:
            self.start_column = start_column
        for letter in text:
            self.draw_letter(letter)

    def draw_letter(self, letter):
        pixels = self.get_letter(letter)
        row_length = len(pixels)
        column_length = len(pixels[0])
        start_column = self.current_column

        for row in range(row_length):
            for column in range(column_length):
                if pixels[row][column]:
                    self.canvas.SetPixel(self.current_column, self.current_row, 0, 255, 0)
                self.current_column += self.increment
            self.current_column = start_column
            self.current_row += self.increment

        self.current_column += column_length * self.increment
        self.current_row = self.line_number

class Matrix(object):
    def __init__(self, columns=128, rows=32, panels=2):
        self.max_columns = columns
        self.max_rows = rows
        self.panels = 1
        self.clear()
        self.forward_lines = []
        self.reverse_lines = []
        self.hardware = Cocktapus()
        self.canvas = self.hardware.canvas
        self.forward_lines.append(LineCursor(self.canvas, 0))
        self.forward_lines.append(LineCursor(self.canvas, 10))
        self.forward_lines.append(LineCursor(self.canvas, 20))

        self.reverse_lines.append(LineCursor(self.canvas, 31, rotated=True))
        self.reverse_lines.append(LineCursor(self.canvas, 21, rotated=True))
        self.reverse_lines.append(LineCursor(self.canvas, 11, rotated=True))

    def reset(self):
        self.forward_lines = []
        self.reverse_lines = []

        self.forward_lines.append(LineCursor(self.canvas, 0))
        self.forward_lines.append(LineCursor(self.canvas, 10))
        self.forward_lines.append(LineCursor(self.canvas, 20))

        self.reverse_lines.append(LineCursor(self.canvas, 31, rotated=True))
        self.reverse_lines.append(LineCursor(self.canvas, 21, rotated=True))
        self.reverse_lines.append(LineCursor(self.canvas, 11, rotated=True))

    def draw_the_line(self, line_number, text,start_column=None):
        
        self.forward_lines[line_number].draw_line(text, start_column)
        self.reverse_lines[line_number].draw_line(text)
        #self.hardware.matrix.SwapOnVSync(self.canvas)

    def show(self):
        #rotated = numpy.rot90(self.pixels[1], 2)
        for row in range(self.max_rows):
            temp = ''
            for column in range(self.max_columns):
                if self.pixels[0][column][row] == 1:
                    temp += '*'
                else:
                    temp += ' '
            #for column in range(self.max_columns):
            #    if rotated[column][row] == 1:
            #        temp += '*'
            #    else:
            #        temp += ' '
            print(temp)


    def clear(self):
        self.pixels = []
        for i in range(self.panels):
            self.pixels.append([])
            self.pixels[i] = zeros((self.max_columns, self.max_rows))

import time
def test():
    m = Matrix()
    start_column = 0
    m.draw_the_line(0, "Life")
    m.draw_the_line(1, "Before")
    m.draw_the_line(2, "Party")
    start_column = 0
    the_text = "Life"
    while True:
        #m.hardware.matrix.Clear()
        #for i in range(3):
        #    m.forward_lines[i].reset()
        #    m.reverse_lines[i].reset()
        #m.draw_the_line(0, "Life")
        #m.draw_the_line(1, "Before")
        #m.draw_the_line(2, "Party")
        #if start_column < 64:
        #    start_column += 1
        #else:
        #    start_column = 0
        #the_text = "Life"
        m.hardware.matrix.Clear() 
        m.reset()        
        #for i in range(3):
        #    m.forward_lines[i].reset()
        #    m.reverse_lines[i].reset()
        method_frame, header_frame, body = channel.basic_get("task_queue")
        if method_frame:
            the_text = body
            print 'Got: %s' % the_text
        print the_text
        m.draw_the_line(0, the_text)
        m.draw_the_line(1, "Before")
        m.draw_the_line(2, "Party") 
        
        
        m.hardware.matrix.SwapOnVSync(m.canvas)
        time.sleep(1)

if __name__ == "__main__":
    test()

