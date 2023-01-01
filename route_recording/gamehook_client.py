from __future__ import annotations
import logging
import copy
import urllib.request
import json
import http.client
import threading
import time
import os

from signalrcore.hub_connection_builder import HubConnectionBuilder, BaseHubConnection

logger = logging.getLogger(__name__)


class GameHookProperty: 
    def __init__(self, client:GameHookClient, data:dict) -> None:
        self._client = client
        self.path = data["path"]
        self.address = data["address"]
        self.length = data["size"]
        self.value = data["value"]
        self.bytes_value = data["bytes"]
        self.frozen = data["frozen"]
    
    """
    TODO: though documented in the API, this is not yet supported
    def set_value(self, value, freeze):
        self._client._edit_property(self.path, freeze, value=value)
    """

    def set_bytes(self, new_bytes, freeze):
        if len(new_bytes) != self.length:
            raise ValueError(f"Cannot set bytes for {self.path} with length {len(new_bytes)}. Must be length {self.length}")
        elif not all([isinstance(x, int) for x in new_bytes]):
            raise ValueError(f"Cannot set bytes for {self.path}, when values are not all ints. Value is: {new_bytes}")
            
        self._client._edit_property(self.path, freeze, new_bytes=new_bytes)
    
    def freeze(self, do_freeze=True):
        if do_freeze:
            self._client._edit_property(self.path, do_freeze, new_bytes=self.bytes_value)
        else:
            self._client._edit_property(self.path, do_freeze)
    
    def change(self, fn):
        if self.path not in self._client._change:
            self._client._change[self.path] = []
        
        self._client._change[self.path].append(fn)
    
    def remove_change(self, fn):
        if self.path in self._client._change:
            try:
                self._client._change[self.path].remove(fn)
            except ValueError:
                logger.warning(f"Tried to remove callback that wasn't present: {fn}")
    
    def once(self, fn):
        if self.path not in self._client._once:
            self._client._once[self.path] = []
        
        self._client._once[self.path].append(fn)
    
    def __repr__(self) -> str:
        return f"{self.path}: {self.value}"

class GameHookClient:
    def __init__(self, connection_string="http://localhost:8085", clear_callbacks_on_load=False) -> None:
        self._connection_string:str = connection_string
        self._clear_callbacks_on_load:bool = clear_callbacks_on_load
        self._signalr_client:BaseHubConnection = None

        self._automatic_refresh_min:int = 1
        self._thread_automatic_refresh = None
        self._thread_background_connect = None

        self._change = {}
        self._once = {}

        self.meta = {}
        self.glossary = {}
        self._ui_configuration = None
        self.properties = {}
        self.connected:bool = False
    
    def is_mapper_loaded(self):
        return len(self.meta) != 0
    
    def _establish_connection(self):
        try:
            self.load_mapper()
            return True
        except Exception as e:
            self.unload_mapper()
            logger.error(f"[GameHook Client] Error encountered trying to establish SignalR connection: {e}")
            logger.exception(e)

            self.on_mapper_load_error(e)

            # TODO: add option for a non-blocking, 5s delayed retry
            # self._establish_connection()
            return False
    
    def connect(self, blocking=False):
        if blocking:
            return self._connect_helper()

        self._thread_background_connect = threading.Thread(
            target=self._connect_helper,
            daemon=True
        )
        self._thread_background_connect.start()
    
    def _connect_helper(self, recreate_client=False):
        try:
            valid_client = True
            if self._signalr_client is None:
                logger.info("[GameHook Client] GameHook Creating SignalR connection from scratch")
                self._signalr_client = HubConnectionBuilder()\
                    .with_url(f"{self._connection_string}/updates")\
                    .configure_logging(logging.WARNING)\
                    .build()

                self._signalr_client.start()

                self._signalr_client.on_close(self._on_disconnect_helper)
                self._signalr_client.on('PropertyChanged', self._on_propery_changed)
                self._signalr_client.on('MapperLoaded', self._on_mapper_loaded)
                self._signalr_client.on('GameHookError', self._on_game_hook_error)
                self._signalr_client.on('DriverError', self._on_driver_error)
                self._signalr_client.on('SendDriverRecovered', self._on_driver_recovered)
                self._signalr_client.on('UiConfigurationChanged', self._on_ui_configuration_change)

                self.connected = True
                self.on_connected()
        except Exception as e:
            valid_client = False
            self._signalr_client = None
            logger.error("[GameHook Client] Exception encountered while building SignlaR connection")
            logger.exception(e)
            self.on_connection_error()

        if valid_client:
            logger.info("[GameHook Client] GameHook successfully established SignalR connection")
            return self._establish_connection()
    
    def disconnect(self):
        logger.info("[GameHook Client] Disconnect called, shutting down SignalR connection")
        self._change = {}
        self._once = {}
        self.meta = {}
        self.glossary = {}
        self._ui_configuration = None
        self.properties = {}
        self.connected = False
        if self._signalr_client is not None:
            # kind of weird, but basically start by un-assigning self._signalr_client to serve as a flag to not reconnect
            client = self._signalr_client
            self._signalr_client = None
            client.stop()

    def _load_mapper_helper(self, propagate_event=False):
        logger.debug("[GameHook Client] Loading mapper")

        with urllib.request.urlopen(f"{self._connection_string}/mapper") as response:
            response:http.client.HTTPResponse
            if response.status != 200:
                response_data = response.read()
                if response_data:
                    msg = f"[GameHook Client] Error loading mapper: {response_data}"
                else:
                    msg = f"[GameHook Client] Error loading mapper"

                logger.error(msg)
                raise ValueError(msg)

            mapper = json.loads(response.read())
        
        self.meta = mapper["meta"]
        self.glossary = mapper["glossary"]
        self.properties = {x["path"]: GameHookProperty(self, x) for x in mapper["properties"]}

        if propagate_event:
            logger.info("[GameHook Client] Mapper loaded successfully!")
            if self._clear_callbacks_on_load:
                self._change = {}
                self._once = {}
            self.on_mapper_loaded()

    def _refresh_mapper_helper(self):
        while True:
            time.sleep(self._automatic_refresh_min * 60)
            if self.is_mapper_loaded():
                self._load_mapper_helper()

    def load_mapper(self):
        # when loading a mapper "manually" (i.e. by direct user invocation)
        # load it manually once, and then configure the auto refresh
        self._load_mapper_helper(propagate_event=True)
        
        # if we haven't started already, kick off the background thread
        if self._thread_automatic_refresh is None:
            self._thread_automatic_refresh = threading.Thread(
                target=self._refresh_mapper_helper,
                daemon=True
            )
            self._thread_automatic_refresh.start()

    def unload_mapper(self):
        logger.info("[GameHook Client] Unloading mapper")
        self.meta = {}
        self.glossary = {}
        self.properties = {}

    def get(self, path):
        return self.properties.get(path)

    def _edit_property(self, path, freeze, new_bytes=None):
        path = path.replace('.', '/')

        # NOTE: if neither value or new_bytes is specified, then default to setting bytes to a null value
        # this is intentional, as it's how we unset the frozen state for a property
        body = json.dumps({"bytes": new_bytes, "freeze": freeze}).encode("utf-8")

        logger.debug(f"Trying to set property with path {path} to {body}")
        req = urllib.request.Request(
            f"{self._connection_string}/mapper/properties/{path}",
            data=body,
            method="PUT",
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req) as response:
            response:http.client.HTTPResponse
            if response.status == 200:
                return
            
            response_data = response.read()
            if response_data:
                msg = f"[GameHook Client] Error setting property {path} with new_bytes {new_bytes}: {response_data}"
            else:
                msg = f"[GameHook Client] Unknown error setting property {path} to new_bytes {new_bytes}"

            logger.error(msg)
            raise ValueError(msg)
    
    ######
    # internal callback methods
    ######
    def _on_disconnect_helper(self):
        logger.warning("[GameHook Client] SignalR connection lost")
        self.unload_mapper()

        self.connected = False
        self.on_disconnected()
        if self._signalr_client is not None:
            logger.warning("[GameHook Client] Attempting automatic reconnection...")
            self._establish_connection()

    def _on_propery_changed(self, args):
        # NOTE: all of the data is passed via a single list, so unpack the list into meaningful values
        [path, address, value, bytes_value, frozen, fields_changed] = args
        if not self.properties:
            logger.debug(f"[GameHook Client] Mapper is not loaded, ignoring PropertUpdated event for: {path}: {value}")
            return
        if path not in self.properties:
            logger.debug(f"[GameHook Client] Could not find a related propery in PropertUpdated event for: {path}: {value}")
            return
        
        new_property = self.properties[path]
        old_property = copy.copy(new_property)

        new_property.address = address
        new_property.value = value
        new_property.bytes_value = bytes_value
        new_property.frozen = frozen

        if "value" in fields_changed:
            if path in self._change:
                for callback_fn in self._change[path]:
                    try:
                        callback_fn(new_property, old_property)
                    except Exception as e:
                        logger.error(f"error encountered running callback_fn: {callback_fn}")
                        logger.exception(e)
            
            if path in self._once:
                for callback_fn in self._once[path]:
                    try:
                        callback_fn(new_property, old_property)
                    except Exception as e:
                        logger.error(f"error encountered running callback_fn: {callback_fn}")
                        logger.exception(e)
                
                self._once[path] = []

        self.on_property_changed(new_property, old_property, fields_changed)
    
    def _on_mapper_loaded(self, args):
        self._load_mapper_helper(propagate_event=True)
    
    def _on_game_hook_error(self, err):
        logger.error(f"[GameHook Client] GameHook error ocurred: {err}")
        self.on_game_hook_error(err)
    
    def _on_driver_error(self, err):
        logger.error(f"[GameHook Client] Driver error ocurred: {err}")
        self.on_driver_error(err)
    
    def _on_driver_recovered(self):
        self.on_driver_recovered()
    
    def _on_ui_configuration_change(self, config):
        self.on_ui_configuration_changed(config)

    ######
    # stubbed methods for subclasses to overwrite
    ######
    def on_connection_error(self):
        pass

    def on_connected(self):
        pass
    
    def on_disconnected(self):
        pass
    
    def on_game_hook_error(self, err):
        pass

    def on_mapper_loaded(self):
        pass

    def on_mapper_load_error(self, err):
        pass

    def on_driver_error(self, err):
        pass

    def on_driver_recovered(self):
        pass

    def on_property_changed(self, property, old_propery, fields_changed):
        pass

    def on_ui_configuration_changed(self, config):
        pass
