from __future__ import annotations


class RecorderController:
    def __init__(self):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def on_mapper_load(self):
        pass

    def on_new_area(self, new_area_name):
        # to make _SOME_ attempt at organization, we're going to track the area
        # whenever a new action is created, if it's in a different area from the last
        # action, then we'll make a new folder for it
        pass

    def on_save(self, location):
        pass

    def on_reset(self):
        pass

    def on_trainer_start(self, trainer_name):
        # NOTE: for now, offloading the work of finding the correct trainer name to the caller of this function
        # So, assuming this trainer_name maps to some valid trainer in the trainer_db
        pass

    def on_trainer_loss(self, trainer_name, defeated_mons):
        # If we initiate a trainer battle, lose to that trainer, and _don't_ reset
        # TODO: need to remove the trainer we lost to from the list
        # TODO: and then add trainer mons of the defeated, so we keep xp, but the trainer is not yet defeated
        pass

    def on_wild_mon_defeated(self, mon_name, level):
        pass

    def on_levelup_move_learned(self, move_name, move_deleted=None):
        pass

    def on_levelup_move_ignored(self, move_name, move_deleted=None):
        pass

    def on_item_pickup(self, item_name, quantity, cost=0):
        pass
    
    def on_generic_item_used(self, item_name, quantity, profit=0):
        pass

    def on_tm_hm_learned(self, move_name, move_deleted=None):
        pass

    def on_rare_candy_used(self, quantity=1):
        pass

    def on_vitamin_used(self, vitamin_name, quantity=1):
        pass


class RecorderModel:
    def __init__(self, controller):
        self._controller = controller
    
    def connect(self):
        pass
    
    def disconnect(self):
        pass