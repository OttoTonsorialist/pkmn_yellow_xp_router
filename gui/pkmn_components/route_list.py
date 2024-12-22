from controllers.main_controller import MainController
import logging

from gui import custom_components
from routing import route_events
from utils.constants import const

logger = logging.getLogger(__name__)


class RouteList(custom_components.CustomGridview):
    def __init__(self, controller:MainController, *args, **kwargs):
        self._controller = controller
        super().__init__(
            *args,
            custom_col_data=[
                custom_components.CustomGridview.CustomColumn('LevelUpsInto', 'get_pkmn_after_levelups', width=220),
                custom_components.CustomGridview.CustomColumn('Level', 'pkmn_level', width=50),
                custom_components.CustomGridview.CustomColumn('Total Exp', 'total_xp', width=80),
                custom_components.CustomGridview.CustomColumn('Exp per sec', 'experience_per_second', width=80),
                custom_components.CustomGridview.CustomColumn('Exp Gain', 'xp_gain', width=80),
                custom_components.CustomGridview.CustomColumn('ToNextLevel', 'xp_to_next_level', width=80),
                custom_components.CustomGridview.CustomColumn('% TNL', 'percent_xp_to_next_level', width=80),
                custom_components.CustomGridview.CustomColumn('event_id', 'group_id', hidden=True),
            ],
            text_field_attr='name',
            semantic_id_attr='group_id',
            tags_attr='get_tags',
            checkbox_attr='is_enabled',
            req_column_width=325,
            #checkbox_callback=self.general_checkbox_callback_fn,
            checkbox_item_callback=self.checkbox_item_callback_fn,
            **kwargs
        )

        # TODO: connect these to the actual style somehow
        self.tag_configure(const.EVENT_TAG_ERRORS, background="#61520f")
        self.tag_configure(const.EVENT_TAG_IMPORTANT, background="#1f1f1f")
        self.tag_configure(const.HIGHLIGHT_LABEL, background="#156152")

        self.bind("<<TreeviewOpen>>", self._treeview_opened_callback)
        self.bind("<<TreeviewClose>>", self._treeview_closed_callback)

    def general_checkbox_callback_fn(self):
        self._controller.get_raw_route()._recalc()
        self.refresh()

    def _treeview_opened_callback(self, *args, **kwargs):
        selected = self.get_all_selected_event_ids()
        # no easy way to figure out unless only one is sleected. Just give up otherwise
        if len(selected) == 1:
            cur_obj = self._controller.get_event_by_id(selected[0])
            if isinstance(cur_obj, route_events.EventFolder):
                cur_obj.expanded = True

            self.refresh()

    def _treeview_closed_callback(self, event):
        selected = self.get_all_selected_event_ids()
        # no easy way to figure out unless only one is sleected. Just give up otherwise
        if len(selected) == 1:
            cur_obj = self._controller.get_event_by_id(selected[0])
            if isinstance(cur_obj, route_events.EventFolder):
                cur_obj.expanded = False

            self.refresh()
    
    def checkbox_item_callback_fn(self, item_id, new_state):
        raw_obj = self._controller.get_event_by_id(self._get_route_id_from_item_id(item_id))
        raw_obj.set_enabled_status(new_state == self.CHECKED_TAG or new_state == self.TRISTATE_TAG)
        self._controller.update_existing_event(raw_obj.group_id, raw_obj.event_definition)
    
    def _get_route_id_from_item_id(self, iid):
        try:
            # super ugly. extract the value of the 'group_id' column. right now this is the last column, so just hard coding the index
            return int(self.item(iid)['values'][-1])
        except (ValueError, IndexError):
            return -1
    
    def set_all_selected_event_ids(self, event_ids):
        new_selection = []
        try:
            for cur_event_id in event_ids:
                new_selection.append(self._treeview_id_lookup[cur_event_id])
            
            self.selection_set(new_selection)
        except Exception as e:
            # This *should* only happen in the case that events are selected which are currently hidden by filters
            # So, just ignore and carry on
            pass
    
    def scroll_to_selected_events(self):
        try:
            if self.selection():
                self.see(self.selection()[-1])
        except Exception as e:
            # NOTE: this seems to happen when the controller creates a new event and immediately selects it
            # in that case, the controller moves faster than the event list, so the event to select it fires before it exists
            # ...maybe. I'm not totally sure. But everything seems fine, so ignore these errors for now
            pass
    
    def get_all_selected_event_ids(self, allow_event_items=True):
        temp = set(self.selection())
        result = []
        for cur_iid in self.selection():
            # event items can't be manipulated at all
            cur_route_id = self._get_route_id_from_item_id(cur_iid)
            if not allow_event_items and isinstance(self._controller.get_event_by_id(cur_route_id), route_events.EventItem):
                continue

            # if any folders are selected, ignore all events that are children of that folder
            # we basically say that you have selected the container, and thus do not need to select any of the child objects
            if self.parent(cur_iid) in temp:
                continue
            
            result.append(cur_route_id)

        return result

    def refresh(self, *args, **kwargs):
        # begin keeping track of the stuff we already know we're displaying
        # so we can eventually delete stuff that has been removed
        to_delete_ids = set(self._treeview_id_lookup.keys())
        self._refresh_recursively("", self._controller.get_raw_route().root_folder.children, to_delete_ids)

        # we have now updated all relevant records, created missing ones, and ordered everything correctly
        # just need to remove any potentially deleted records
        for cur_del_id in to_delete_ids:
            try:
                self.delete(self._treeview_id_lookup[cur_del_id])
            except Exception:
                # note: this occurs because deleting an entry with children automatically removes all children too
                # so it will fail to remove the children aftewards
                # No actual problem though, just remove from the lookup and continue
                pass
            del self._treeview_id_lookup[cur_del_id]

        self.event_generate(const.ROUTE_LIST_REFRESH_EVENT)
    
    def _refresh_recursively(self, parent_id, event_list, to_delete_ids:set):
        cur_search = self._controller.get_route_search_string()
        cur_filter = self._controller.get_route_filter_types()
        for event_idx, event_obj in enumerate(event_list):
            semantic_id = self._get_attr_helper(event_obj, self._semantic_id_attr)

            if not event_obj.do_render(
                search=cur_search,
                filter_types=cur_filter,
            ):
                continue

            if isinstance(event_obj, route_events.EventFolder):
                is_folder = True
                force_open = event_obj.expanded
            else:
                is_folder = False
                force_open = False

            if semantic_id in to_delete_ids:
                to_delete_ids.remove(semantic_id)
                cur_event_id = self._treeview_id_lookup[semantic_id]
                self.custom_upsert(event_obj, parent=parent_id, force_open=force_open, update_checkbox=True)
            else:
                # when first creating the event, make sure it is defined with a checkbox
                cur_event_id = self.custom_upsert(event_obj, parent=parent_id, force_open=force_open, update_checkbox=True)

            if self.index(cur_event_id) != event_idx or self.parent(cur_event_id) != parent_id:
                self.move(cur_event_id, parent_id, event_idx)

            if is_folder:
                self._refresh_recursively(cur_event_id, event_obj.children, to_delete_ids)

            elif isinstance(event_obj, route_events.EventGroup):
                if len(event_obj.event_items) > 1:
                    for item_idx, item_obj in enumerate(event_obj.event_items):
                        item_semantic_id = self._get_attr_helper(item_obj, self._semantic_id_attr)
                        if item_semantic_id in to_delete_ids:
                            item_id = self._treeview_id_lookup[item_semantic_id]
                            to_delete_ids.remove(item_semantic_id)
                            self.custom_upsert(item_obj, parent=cur_event_id)
                        else:
                            item_id = self.custom_upsert(item_obj, parent=cur_event_id)

                        if self.index(cur_event_id) != item_idx or self.parent(cur_event_id) != cur_event_id:
                            self.move(item_id, cur_event_id, item_idx)