
def dict_has_key(dict, key):
    try:
        dict[key]
        return True
    except KeyError:
        return False


dict = {
    "hello": {
        "test": 10,
        "test1": 0
    },
    "hello2": {
        "test": 0,
        "test1": 0
    }
}

for entry in dict:
    if dict[entry]["test"] == 10:
        print(entry)