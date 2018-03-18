"""

Data layer.

{"action": <add, delete, edit show>,
 "index": <int>.
 "data": {"display_time": <int>,
          "line1": {"text": <str>,
                    "color": [<int>]
                    },
          "line2": {"text": <str>,
                    "color": [<int>]
                    },
          "line3": {"text": <str>,
                    "color": [<int>]
                    },
        }
}

"""


"""Standard Modules."""
import json


"""Project Modules."""
import defines
import colors


def write_to_disk(data, filename):
    
    if type(data) is list:
        data = {'entries': data}
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)


def read_from_disk(filename):
    try:
        with open(filename) as json_data:
            d = json.load(json_data)
            return d['entries']
    except:
        return []


class Line(object):
    def __init__(self, text, color):
        self.text = text
        self.color = color

    def serialize(self):
        return {"text": self.text,
                "color": self.color}


class Entry(object):
    def __init__(self):
        self.lines = []
        self.display_time = defines.default_display_time

    def deserialize(self, data):
        entry = data['data']

        line1 = Line(entry['line1']['text'],
                     entry['line1']['color'])

        line2 = Line(entry['line2']['text'],
                     entry['line2']['color'])

        line3 = Line(entry['line3']['text'],
                     entry['line3']['color'])

        self.lines.append(line1)
        self.lines.append(line2)
        self.lines.append(line3)

    def serialize(self):
        output = {"display_time": self.display_time,
                  "line1": self.lines[0].serialize(),
                  "line2": self.lines[1].serialize(),
                  "line3": self.lines[2].serialize()}
        return output


class DataStore(object):
    """Data Store for sign data."""

    def __init__(self, filename, input_queue,
                 output_queue):
        self.data = []
        self.filename = filename
        self.current_index = 0
        self.input_queue = input_queue
        self.output_queue = output_queue
        self._load()

    def serialize(self):
        return {"entries": self.data}

    def _load(self):
        self.data = read_from_disk(self.filename)

    def _save(self):
        write_to_disk(self.data, self.filename)

    def _reload(self):
        self._save()
        self._load()

    def _add(self, data):
        if not data['display_time']:
            data['display_time'] = defines.default_display_time

        self.data.append(data)
        self._reload()

    def _insert(self, data, index):
        self.data.insert(data, index)
        self._reload()

    def _remove(self, index):
        self.data.pop(index)
        self._reload()

    def get(self, index=None):
        if index:
            return self.data[index]
        else:

            if not (self.current_index < len(self.data)):
                self.current_index = 0

            output = self.data[self.current_index]
            self.current_index += 1
            return output

    def update(self):
        data = self.input_queue.get()

        action = data['action']

        if action == "add":
            self._add(data['data'])

        elif action == "delete":
            index = data['index']
            self._remove(index)

        elif action == "edit":
            index = data['index']
            #self.remove(index)
            self._insert(data['data'], index)
            self.data[index] = data['data']

        elif action == "move":
            source = data['source_index']
            dest = data['destination_index']
            self.data[dest] = self.data[source]
            self._remove(source)

        elif action in ["show", "preview"]:
            self.output_queue.put(data)

        self.input_queue.task_done()











