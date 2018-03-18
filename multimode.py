"""Cache for persistance."""


"""Standard Libraries."""
import time
import json
import thread
from Queue import Queue
from flask import Flask, jsonify, request, render_template

"""Project libraries."""
import colors
import defines
from data_layer import DataStore
from display import SimpleDisplay


class UpdateQueue(Queue):
    """
    Queue for updates.

    Passes updates between web
    server and Data Store.
    """

    pass


class EventQueue(Queue):
    """
    Queue for events.

    Passes events from Data Store
    to the Controller.
    """

    pass


class DisplayQueue(Queue):
    """
    Queue for display updates.

    Passes events from Controller
    to the Display.
    """

    pass




from pprint import pprint
class Controller(object):
    """Handles processing updates to display."""

    def __init__(self, mode, input_queue,
                 output_queue, data_store):
        self.mode = mode
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.data_store = data_store

    def set_mode(self, mode):
        self.mode = mode

    def in_display_mode(self):
        return self.mode == defines.display_mode

    def update(self):
        entry = self.input_queue.get()

        if entry['action'] in [defines.show, "preview"]:
            self.output_queue.put(entry)
            # print "@ "
            # pprint(entry)
        elif self.in_display_mode():
            data = self.data_store.get()
            command = {"action": "show",
                       "data": data}
            # print command
            self.output_queue.put(command)

        self.input_queue.task_done()


class Display(object):

    def __init__(self, input_queue, data_store):
        self.input_queue = input_queue
        self.display = SimpleDisplay()
        self.data_store = data_store

    def update(self):
        entry = self.input_queue.get()
        # print(entry)
        #if entry['action'] == defines.show:
        if 'index' in entry:
            entry = self.data_store.get(entry['index'])
        print entry
        self.write_to_display(entry)
        self.input_queue.task_done()

    def write_to_display(self, data):
        # pprint(data.keys())
        if 'data' in data:
            data = data['data']
        lines = [data['line1']['text'],
                 data['line2']['text'],
                 data['line3']['text']]

        for (index, item) in enumerate(lines):
            if item == "":
                lines[index] = " "
        colors = [data['line1']['color'],
                  data['line2']['color'],
                  data['line3']['color']]

        print data
        if data['display_time']:
            display_time = data['display_time']
        else:
            display_time = defines.default_display_time

        self.display.write_all_lines(lines, display_time, colors)

"""Global variables."""
update_queue = UpdateQueue()
event_queue = EventQueue()
display_queue = DisplayQueue()
app = Flask(__name__)

data_store = DataStore(defines.default_filename,
                       update_queue, event_queue)
controller = Controller(defines.display_mode, event_queue,
                        display_queue, data_store)
display = Display(display_queue, data_store)


""" Web Interface."""
@app.route("/update", methods=["POST"])
def update():
    print(request.json)
    update_queue.put(request.json)
    return jsonify({'result': True})

@app.route('/view')
def view():
    return render_template("view.html")

@app.route('/show/<int:index>')
def show(index):
    #global editor_queue
    # editor_queue.append(index)
    message = {"action": "show",
               "index": index}
    update_queue.put(message)

    return jsonify({"result": True})

@app.route("/")
def hello():
    return jsonify(data_store.serialize())

@app.route('/mode/<mode>')
def set_mode(mode):
    controller.set_mode(mode)
    return jsonify({'result': True})

def flask_thread():
    app.run(host='0.0.0.0', debug=False)

def main_loop():
    # data_store.set_mode(mode)
    # controller.set_mode(mode)
    """
    data_store = DataStore(defines.default_filename,
                           update_queue, event_queue)
    controller = Controller(mode, event_queue, display_queue,
                            data_store)
    display = Display(display_queue)
    """
    while True:
        # Pass any updates from the web interface
        # to the data store.
        if not update_queue.empty():
            data_store.update()
        
        # Pass any updates from the data store
        # to the controller.
        if not event_queue.empty():
            controller.update()

        # If we're in display mode enqueue
        # the next entry
        if controller.in_display_mode():
            display_queue.put(data_store.get())

        # Pass any updates from the controller
        # to the display
        if not display_queue.empty():
            display.update()
    

def run_display():
    main_loop(defines.display_mode)


def run_editor():
    main_loop(defines.editor_mode)





if __name__ == "__main__":
    thread.start_new_thread(flask_thread, ())
    # run_display()
    # run_editor()
    main_loop()






