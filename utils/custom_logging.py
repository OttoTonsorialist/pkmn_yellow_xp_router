import os
import logging


def config_logging(base_log_dir):
    formatter = logging.Formatter('%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s')

    file_handler = logging.FileHandler(os.path.join(base_log_dir, "pkmn_router_logs.log"))
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    _logger = logging.getLogger()
    _logger.setLevel(logging.INFO)
    _logger.addHandler(file_handler)
    _logger.addHandler(stream_handler)