
def save_settings():

    file = open('settings.txt', 'w')
    for key, value in settings.items():
        file.write(key + ': ' + str(value) + '\n')
    file.close()


def settings_to_dict():
    file = open('settings.txt', 'r')
    dictionary = {}
    for line in file.readlines():
        args = line.split(':')
        key = args[0].strip()
        value = args[1].strip()
        dictionary.update({key: value})

    return dictionary


settings = settings_to_dict()
