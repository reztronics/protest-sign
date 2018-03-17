from display import ThreeLineDisplay
import time

import json
import thread

from flask import Flask, jsonify, request, render_template


app = Flask(__name__)

cache = {}
update_queue = []


def write_to_disk(data):
    pass

    with open('/protest/data.json', 'w') as outfile:
        json.dump(data, outfile)

def read_from_disk():
    try:
        with open('/protest/data.json') as json_data:
            d = json.load(json_data)
            return d
    except:
        return {"entries": []}

@app.route("/")
def hello():
    return jsonify(cache)

@app.route("/test")
def test():
    return jsonify({"updates": update_queue})

@app.route("/view")
def view():
    return render_template("view.html")

@app.route('/update', methods=['POST'])
def update():
    print request.json
    update_queue.append(request.json)
    return jsonify(request.json)

def flaskThread():
    app.run(host='0.0.0.0', debug=False)

thread.start_new_thread(flaskThread,())

YELLOW = (255, 255, 0)
PINK = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

def color_from_string(s):
    if s == 'yellow':
        return YELLOW
    elif s == "pink":
        return PINK
    elif s == "red":
        return RED
    elif s == "green":
        return GREEN
    elif s == "blue":
        return BLUE
    else:
        return RED

WAIT_TIME = 2.0



class SimpleDisplay(ThreeLineDisplay):

    def reset_all_lines(self):
        for i in [0, 1, 2]:
            self.reset_line(i)
            self.clear_line(i)

    def write_one_line(self, line_number, text, color, wait=WAIT_TIME):
        self.reset_line(line_number)
        self.clear_line(line_number)
        self.draw_the_line(line_number=line_number, text=text, color=color)
        time.sleep(wait)

    def write_all_lines(self, lines, wait=WAIT_TIME, colors=[GREEN, YELLOW, PINK]):
        self.reset_all_lines()
        self.draw_the_line(line_number=0, text=lines[0], color=colors[0])
        self.draw_the_line(line_number=1, text=lines[1], color=colors[1])
        self.draw_the_line(line_number=2, text=lines[2],  color=colors[2])
        self.update()
        time.sleep(wait)


class Line(object):
    def __init__(self, text, color):
        self.text = text
        self.color = color

    def to_json(self):
        return {"text": self.text, "color": self.color}

class Entry(object):
    def __init__(self, line_1_text, line_1_color,
                 line_2_text, line_2_color,
                 line_3_text, line_3_color,
                 display_time):

        self.lines = [Line(line_1_text, line_1_color),
                      Line(line_2_text, line_2_color),
                      Line(line_3_text, line_3_color)]

        self.display_time = display_time

    def get_lines(self):
        return [self.lines[0].text,
                self.lines[1].text,
                self.lines[2].text]

    def get_colors(self):
        return [self.lines[0].color,
                self.lines[1].color,
                self.lines[2].color]

    def to_json(self):
        output = {}
        output['line1'] = self.lines[0].to_json()
        output['line2'] = self.lines[1].to_json()
        output['line3'] = self.lines[2].to_json()
        output[ 'display_time'] = self.display_time
        return output

class Script(object):
    def __init__(self):
        self.display = SimpleDisplay()
        print "Starting"
        self.reload()

    def reload(self):
        data = read_from_disk()
        print 'read from disk'
        self.entries = []
        for entry in data['entries']:
            self.entries.append(Entry(entry['line1']['text'],
                                      entry['line1']['color'],
                                      entry['line2']['text'],
                                      entry['line2']['color'],
                                      entry['line3']['text'],
                                      entry['line3']['color'],
                                      entry['display_time']))

    def to_json(self):
        return {"entries": [k.to_json() for k in self.entries]}

    def update_cache(self):
        global cache
        
        cache = self.to_json()
        write_to_disk(cache)
        self.reload()

    def add_entry(self, entry, index=None):
        """Add entry."""
        if index:
            self.entries.insert(index, entry)
        else:
            self.entries.append(entry)

    def get_updates(self):
        """Get any pending updates."""
        if update_queue:
            return update_queue.pop()

    def draw_entry(self, entry):
        """Draw an entry."""
        self.display.write_all_lines(
            entry.get_lines(),
            wait=entry.display_time,
            colors=entry.get_colors())

    def run(self):
        """Play the script."""
        while True:
            updates = self.get_updates()
            if updates:
                self.update(updates)

            for entry in self.entries:
                self.draw_entry(entry)


    def remove_entry(self, index):
        """Remove entry."""
        try:
            self.cache['entries'].pop(index)
            self.entries.pop(index)
            # self.update_cache()
        except Exception:
            print 'There was an error removing an entry'

    def update(self, data):
        """Update the script."""
        #data = json.loads(data)
        if 'index' in data:
            index = data['index']
        else:
            index = None

        if data['action'] == 'add':
            line_1_text = data['line1']['text']
            line_1_color = color_from_string(data['line1']['color'])
            line_2_text = data['line2']['text']
            line_2_color = color_from_string(data['line2']['color'])
            line_3_text = data['line3']['text']
            line_3_color = color_from_string(data['line3']['color'])
            
            if not type(data['display_time']) is int:
                data['display_time'] = 1
            
            display_time = data['display_time']

            entry = Entry(line_1_text, line_1_color,
                          line_2_text, line_2_color,
                          line_3_text, line_3_color,
                          display_time)
            self.add_entry(entry, index)

        elif data['action'] == 'delete':
            index = data['index']
            self.remove_entry(index)

        self.update_cache()



#if __name__ == "__main__":
s = Script()
s.run()
