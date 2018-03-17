"""Cache for persistance."""


from display import ThreeLineDisplay
import time

import json
import thread

from flask import Flask, jsonify, request, render_template


YELLOW = (255, 255, 0)
PINK = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

WAIT_TIME = 2

app = Flask(__name__)
update_queue = []
editor_queue = []
edit_entry_queue = []

"""
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
"""


def write_to_disk(data):
    
    if type(data) is list:
        data = {'entries': data}
    with open('/protest/data.json', 'w') as outfile:
        json.dump(data, outfile)


def read_from_disk():
    try:
        with open('/protest/data.json') as json_data:
            d = json.load(json_data)
            return d['entries']
    except:
        return []


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
        self.text = text if text else " "
        self.color = color

    def to_json(self):
        return {"text": self.text, "color": self.color}


class Entry(object):
    def __init__(self):
        self.display_time = 3
        self.lines = []

    def from_json(self, data):
        """Load data from JSON action request"""
        self.lines.append(Line(
            data['line1']['text'],
            data['line1']['color']))

        self.lines.append(Line(
            data['line2']['text'],
            data['line2']['color']))

        self.lines.append(Line(
            data['line3']['text'],
            data['line3']['color']))
        if data['display_time']:
            self.display_time = data['display_time']

    def to_json(self):
        output = {}
        output['line1'] = self.lines[0].to_json()
        output['line2'] = self.lines[1].to_json()
        output['line3'] = self.lines[2].to_json()
        output[ 'display_time'] = self.display_time
        return output

    def get_lines(self):
        return [self.lines[0].text,
                self.lines[1].text,
                self.lines[2].text]

    def get_colors(self):
        return [self.lines[0].color,
                self.lines[1].color,
                self.lines[2].color]

class Cache(object):
    def __init__(self):
        self.data = []
        self.load()
        self.flag = False

    def has_update(self):
        return self.flag

    def set_flag(self):
        self.flag = True

    def reset_flag(self):
        self.flag = False

    def clear(self):
        """Clear the cache."""
        self.data = []

    def load(self):
        self.data = read_from_disk()

    def reload(self):
        """Reload cache from disk."""
        self.save()
        self.load()

    def save(self):
        """Save cache to disk."""
        write_to_disk(self.data)

    def remove_entry(self, index):
        """Remove entry."""
        try:
            self.data.pop(index)
        except Exception:
            print 'Error deleting entry at index %s' % index
        self.reload()

    def get_entries(self):
        """Return a list of Entry objects."""
        self.reload()
        output = []
        for entry in self.data:
            e = Entry()
            e.from_json(entry)
            output.append(e)
        return output

    def to_json(self):
        """Return JSON representation."""
        return {"entries": self.data}

    def edit_entry(self, data, index):
        """Edit an existing item."""
        print type(index), index, data
        temp = self.data.pop(index)
        if 'action' in data:
            del data['action']
        self.data.insert(data, index)

    def add_entry(self, data, index=None):
        """Add an entry to the cache."""
        if 'action' in data:
            del data['action']
        if index:
            self.data.insert(data, index)
        else:
            self.data.append(data)
        self.reload()





class Script(object):
    """The sign script."""

    def __init__(self):
        """Constructor."""
        self.display = SimpleDisplay()
        print 'Starting'

    def draw_entry(self, entry):
        """Draw an entry."""
        self.display.write_all_lines(
            entry.get_lines(),
            wait=entry.display_time,
            colors=entry.get_colors())

    def reload(self):
        cache.reload()

    def to_json(self):
        """Return JSON representation."""
        global cache
        return cache.to_json()

    def get_updates(self):
        """Get any pending updates."""
        if update_queue:
            return update_queue.pop()

    def check_for_update(self):
        updates = self.get_updates()
        if updates:
            self.update(updates)
            self.display.reset_all_lines()
            return True
        else:
            return False

    def run_editor(self):
        while True:
            if edit_entry_queue:
                data = edit_entry_queue.pop()
                cache.edit_entry(data, data['index'])

            elif cache.has_update():
                cache.reset_flag()

            elif editor_queue:
                index = editor_queue.pop()
                entries = cache.get_entries()
                try:
                    if index == 0:
                        entry = entries[0]
                    else:
                        entry = entries[index%len(entries)]
                    self.draw_entry(entry)
                except Exception as e:
                    pass

    def run(self):
        """Play the script."""
        while True:
            #updates = self.get_updates()
            #if updates:
            #    self.update(updates)
            #self.display.reset_all_lines()
            for entry in cache.get_entries():
                if cache.has_update():
                    cache.reset_flag()
                    break
                else:
                    self.draw_entry(entry)
                #if self.check_for_update():
                #    break
                #else:
                #    self.draw_entry(entry)

    def update(self, data):
        """Update."""
        if data['action'] == 'add':
            if 'index' in data:
                cache.add_entry(data['data'], index)
            else:
                cache.add_entry(data['data'])

        elif data['action'] == 'delete':
            index = data['index']
            cache.remove_entry(index)
            #self.display.reset_all_lines()

        elif data['action'] == "edit":
            index = data['index']
            cache.edit_entry(index, data)


cache = Cache()
s= Script() 

@app.route('/show/<int:index>')
def show(index):
    #global editor_queue
    editor_queue.append(index)
    return jsonify({"result": True})

@app.route("/")
def hello():
    return jsonify(cache.to_json())

@app.route("/test")
def test():
    return jsonify({"updates": update_queue})

@app.route("/view")
def view():
    return render_template("view.html")

@app.route("/edit", methods=["POST"])
def edit_entry():
    print request.json
    data = request.json
    edit_entry_queue.append(data)
    #index = int(data['index'])
    #print " ***************** %s **********" % index
    #cache.edit_entry(data, index)
    return jsonify(request.json)

@app.route('/update', methods=['POST'])
def update():
    print request.json
    #update_queue.append(request.json)
    data = request.json
    if data['action'] == 'add':
        if 'index' in data:
            cache.add_entry(data['data'], index)
        else:
            cache.add_entry(data['data'])

    elif data['action'] == 'delete':
        index = data['index']
        cache.remove_entry(index)

    cache.set_flag()

    return jsonify(request.json)

def flaskThread():
    app.run(host='0.0.0.0', debug=False)

thread.start_new_thread(flaskThread,())



if __name__ == "__main__":
    #s.run_editor()
    s.run()

