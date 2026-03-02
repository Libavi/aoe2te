def load(file_):
    items = {}
    for line in file_:
        line = line.strip()
        if not line or line.startswith("//"):
            continue

        key, value = line.split(None, 1)
        value = value.strip().strip('"')
        items[key] = value

    return items


def dump(dict_, file_):
    for key, value in dict_.items():
        file_.write(f"{key} \"{value}\"\n")
