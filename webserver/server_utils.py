from typing import Dict, List
from flask import request

from pkmn.universal_data_objects import Nature
from utils.constants import const


def simple_result(val, key="result"):
    return {
        key: val,
    }, 200


def parse_str(name, default=None, optional=True) -> int:
    if name not in request.args:
        if not optional:
            raise ValueError(f"Missing required parameter: {name}")
        return default

    return request.args.get(name, default)


def parse_str_list(name, default=None, optional=True, separator=",") -> int:
    if name not in request.args:
        if not optional:
            raise ValueError(f"Missing required parameter: {name}")
        return default

    raw_val = request.args.get(name, default)
    return [x.strip() for x in raw_val.split(separator) if x.strip()]


def parse_int_list(name) -> List[int]:
    result = [x.strip() for x in request.args.get(name, "").split(",")]
    try:
        target_ids = [int(x) for x in target_ids]
    except Exception as e:
        raise ValueError(f"Could not convert {name} to ints: {target_ids}")

    return result


def parse_int(name, default=None, optional=True) -> int:
    if name not in request.args:
        if not optional:
            raise ValueError(f"Missing required parameter: {name}")
        return default

    raw_val = request.args.get(name, default)
    try:
        return int(raw_val)
    except Exception as e:
        raise ValueError(f"Could not convert {name} to int: {raw_val}")


def parse_bool_int(name, default=False, optional=True) -> bool:
    if name not in request.args:
        if not optional:
            raise ValueError(f"Missing required parameter: {name}")
        return default

    raw_val = request.args.get(name, default)
    try:
        return bool(int(raw_val))
    except Exception as e:
        raise ValueError(f"Could not convert {name} to bool: {raw_val}")


def parse_nature_int(name, default=None, optional=True) -> Nature:
    if name not in request.args:
        if not optional:
            raise ValueError(f"Missing required parameter: {name}")
        return default

    raw_val = request.args.get(name, default)
    try:
        return Nature(int(raw_val))
    except Exception as e:
        raise ValueError(f"Could not convert {name} to Nature: {raw_val}")


def deseralize_json(out_type):
    try:
        return out_type.deserialize(request.json)
    except Exception as e:
        raise ValueError(f"Failed to deserialize json to type {out_type} due to exception: {e}")


def validate_raw_stat_block(raw_input, optional=True) -> Dict[str, int]:
    if not raw_input:
        if optional:
            return None

        raise ValueError(f"Stat block was not provided")

    req_keys = [
        const.HP,
        const.ATTACK,
        const.DEFENSE,
        const.SPECIAL_ATTACK,
        const.SPECIAL_DEFENSE,
        const.SPEED,
    ]
    missing_keys = []
    wrong_type = []
    result = request.json

    for cur_key in req_keys:
        if cur_key not in result:
            missing_keys.append(cur_key)
            continue

        if not isinstance(result[cur_key], int):
            wrong_type.append(f"{cur_key}: {result[cur_key]}")

    errors = []
    if missing_keys:
        errors.append(f"The following keys are missing: {','.join(missing_keys)}")

    if wrong_type:
        errors.append(f"The following keys have invalid data: {', '.join(wrong_type)}")

    if errors:
        raise ValueError("Could not validate raw stat block. " + f". ".join(errors))

    return result
