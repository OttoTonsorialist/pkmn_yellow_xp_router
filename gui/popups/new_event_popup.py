import tkinter as tk

from controllers.main_controller import MainController
from gui.popups.base_popup import Popup
from gui import custom_tkinter, route_event_components, pkmn_components
from utils.constants import const


class NewEventWindow(Popup):
    def __init__(self, main_window, controller:MainController, cur_defeated_trainers, cur_state, *args, insert_after=None, **kwargs):
        super().__init__(main_window, controller, *args, **kwargs, width=700, height=600)
        self._controller = controller
        self._insert_after = insert_after
        self._cur_defeated_trainers = cur_defeated_trainers
        self._cur_state = cur_state

        self.title("Create New Event")
        self._top_pane = tk.Frame(self)
        self._top_pane.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

        self._state_viewer = pkmn_components.StateViewer(self._top_pane)
        self._state_viewer.grid(row=0, column=0)
        self._state_viewer.set_state(cur_state)

        self._input_frame = tk.Frame(self._top_pane, width=700, height=600)
        self._input_frame.grid(row=1, column=0)
        self._input_frame.grid_propagate(False)

        # elements going inside the frame
        self._event_type_label = tk.Label(self._input_frame, text="Event:")
        self._event_type_label.grid(row=0, column=0)
        self._event_type = custom_tkinter.SimpleOptionMenu(self._input_frame, const.ROUTE_EVENT_TYPES, callback=self._event_type_callback)
        self._event_type.grid(row=0, column=1)

        self._create_new_event_button = custom_tkinter.SimpleButton(self, text="Add Event", command=self._new_event)
        self._create_new_event_button.grid(row=1, column=0)
        self._create_new_event_button.disable()

        self._cancel_button = custom_tkinter.SimpleButton(self, text="Cancel", command=self.close)
        self._cancel_button.grid(row=1, column=1)
        self._cancel_button.enable()

        self._event_editor_lookup = route_event_components.EventEditorFactory(self._input_frame, self._create_new_event_button)
        self._cur_editor:route_event_components.EventEditorBase = None

        self.bind('<Return>', self._new_event)
        self.bind('<Escape>', self.close)
        self._event_type.focus_set()
        self._event_type_callback()

    def _event_type_callback(self, *args, **kwargs):
        new_event_type = self._event_type.get()

        # otherwise, hide our current editor, and get the new one
        if self._cur_editor is not None:
            self._cur_editor.grid_remove()
        
        self._cur_editor = self._event_editor_lookup.get_editor(
            route_event_components.EditorParams(
                new_event_type,
                self._cur_defeated_trainers,
                self._cur_state,
            )
        )
        self._cur_editor.grid(row=1, column=0, columnspan=2)

    def _new_event(self, *args, **kwargs):
        self.close()
        self._controller.new_event(self._cur_editor.get_event(), insert_after=self._insert_after)
