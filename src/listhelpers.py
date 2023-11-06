from typing import Any


def upsert_list(list_object: list, item: Any, index: int) -> bool:
    length = len(list_object)

    if index > length or index < 0:
        return False

    if index == length:
        list_object.append(item)
    elif index < length:
        list_object[index] = item

    return True
