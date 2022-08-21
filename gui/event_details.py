import tkinter as tk
from tkinter import ttk

from gui import custom_tkinter, route_event_components, pkmn_components, quick_add_components
from pkmn.route_events import EventDefinition, EventFolder, EventGroup, EventItem, InventoryEventDefinition, LearnMoveEventDefinition, RareCandyEventDefinition, TrainerEventDefinition, VitaminEventDefinition
from pkmn.router import Router
from utils.constants import const
import pkmn.pkmn_db as pkmn_db


class EventDetails(tk.Frame):
    def __init__(self, *args, event_update_callback=None, **kwargs):
        super().__init__(*args, **kwargs, width=900)

        self.event_update_callback = event_update_callback
        self._cur_trainer_name = None

        self.tabbed_states = ttk.Notebook(self)

        self.pre_state_frame = tk.Frame(self.tabbed_states)
        self.pre_state_frame.pack(fill=tk.X)
        self.state_pre_label = tk.Label(self.pre_state_frame, text="Pre-event State Display Mode:")
        self.state_pre_label.grid(column=1, row=0, padx=10, pady=10)
        self.pre_state_selector = custom_tkinter.SimpleOptionMenu(self.pre_state_frame, [const.STATE_SUMMARY_LABEL, const.BADGE_BOOST_LABEL], callback=self._pre_state_display_mode_callback)
        self.pre_state_selector.grid(column=2, row=0, padx=10, pady=10)
        self.state_pre_viewer = pkmn_components.StateViewer(self.pre_state_frame)
        self.state_pre_viewer.grid(column=1, row=1, padx=10, pady=10, columnspan=2)
        self.badge_boost_viewer = pkmn_components.BadgeBoostViewer(self.pre_state_frame)

        self.pre_state_frame.columnconfigure(0, weight=1)
        self.pre_state_frame.columnconfigure(3, weight=1)

        self.post_state_frame = tk.Frame(self.tabbed_states)
        self.post_state_frame.pack()
        self.state_post_label = tk.Label(self.post_state_frame, text="Post-event State:")
        self.state_post_label.grid(column=1, row=0, padx=10, pady=10)
        self.state_post_viewer = pkmn_components.StateViewer(self.post_state_frame)
        self.state_post_viewer.grid(column=1, row=1, padx=10, pady=10)

        self.tabbed_states.add(self.pre_state_frame, text="Pre-event State")
        self.tabbed_states.add(self.post_state_frame, text="Post-event State")
        self.tabbed_states.pack(anchor=tk.N, fill=tk.X, padx=5, pady=5)

        self.event_viewer_frame = tk.Frame(self, highlightbackground="black", highlightthickness=2)
        self.event_viewer_frame.pack(anchor=tk.N, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.event_details_frame = tk.Frame(self.event_viewer_frame)
        self.event_details_frame.grid(row=0, column=0)

        self.footer_frame = tk.Frame(self.event_viewer_frame)
        self.footer_frame.grid(row=1, column=0, sticky=tk.EW)

        self.enemy_team_viewer = pkmn_components.EnemyPkmnTeam(self.event_details_frame)
        self.enemy_team_viewer.pack()

        # create this slightly out of order because we need the reference
        self.event_details_button = custom_tkinter.SimpleButton(self.footer_frame, text="Save", command=self.update_existing_event)
        self.verbose_trainer_label = custom_tkinter.CheckboxLabel(self.footer_frame, text="Verbose Route1 Export", toggle_command=self.update_existing_event)
        self.event_editor_lookup = route_event_components.EventEditorFactory(self.event_details_frame, self.event_details_button)
        self.current_event_editor = None

        self.stat_info_label = tk.Label(self.footer_frame, text="Stats with * are calculated with a badge boost")
        self.stat_info_label.config(bg="white")
        self.stat_info_label.grid(row=1, column=0, columnspan=2)

        self.trainer_notes = route_event_components.EventEditorFactory(self.footer_frame, self.event_details_button).get_editor(
            route_event_components.EditorParams(const.TASK_NOTES_ONLY, None, None)
        )
        self.trainer_notes.grid(row=2, column=0, columnspan=2, sticky=tk.EW)

        self.event_details_button.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.event_details_button.disable()

        self.event_viewer_frame.rowconfigure(0, weight=1)
        self.event_viewer_frame.columnconfigure(0, weight=1)

        self.footer_frame.columnconfigure(1, weight=1)

    def _pre_state_display_mode_callback(self, *args, **kwargs):
        if self.pre_state_selector.get() == const.BADGE_BOOST_LABEL:
            self.state_pre_viewer.grid_forget()
            self.badge_boost_viewer.grid(column=1, row=1, padx=10, pady=10, columnspan=2)
        else:
            self.badge_boost_viewer.grid_forget()
            self.state_pre_viewer.grid(column=1, row=1, padx=10, pady=10, columnspan=2)
    
    def toggle_trainer_verbosity(self, new_val):
        pass
    
    def show_event_details(self, event_def:EventDefinition, init_state, final_state, allow_updates=True):
        self.state_pre_viewer.set_state(init_state)
        self.badge_boost_viewer.set_state(init_state)

        self.state_post_viewer.set_state(final_state)
        self._cur_trainer_name = None

        if self.current_event_editor is not None:
            self.current_event_editor.pack_forget()
            self.current_event_editor = None

        if event_def is None:
            self.enemy_team_viewer.set_team(None)
            self.trainer_notes.load_event(None)
            self.enemy_team_viewer.pack_forget()
            self.verbose_trainer_label.grid_forget()
            self.event_details_button.disable()
        else:
            if allow_updates:
                self.event_details_button.enable()
            else:
                self.event_details_button.disable()

            self.trainer_notes.load_event(event_def)

            if event_def.trainer_def is not None:
                self._cur_trainer_name = event_def.trainer_def.trainer_name
                self.enemy_team_viewer.pack()
                self.enemy_team_viewer.set_team(event_def.get_trainer_obj().pkmn, cur_state=init_state)
                self.verbose_trainer_label.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
                self.verbose_trainer_label.set_checked(event_def.trainer_def.verbose_export)
            else:
                self.enemy_team_viewer.pack_forget()
                self.enemy_team_viewer.set_team(None)
                self.verbose_trainer_label.grid_forget()

                # TODO: fix this gross ugly hack
                self.current_event_editor = self.event_editor_lookup.get_editor(
                    route_event_components.EditorParams(event_def.get_event_type(), None, init_state,)
                )
                self.current_event_editor.load_event(event_def)
                self.current_event_editor.pack()

    def update_existing_event(self, *args, **kwargs):
        try:
            if self.current_event_editor is None:
                new_event = EventDefinition(trainer_def=TrainerEventDefinition(self._cur_trainer_name, verbose_export=self.verbose_trainer_label.is_checked()))
            else:
                new_event = self.current_event_editor.get_event()
            
            new_event.notes = self.trainer_notes.get_event().notes
        except Exception as e:
            new_event = None
        
        if self.event_update_callback is not None:
            self.event_update_callback(new_event)
    