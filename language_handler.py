
def get_message(field, language):
    """
    Get the value of a key of a language dictionary.

    :param field: key
    :param language: language code name (iso 639-1)
    :return: message (str)
    """
    if language == 'es':
        return es_dict.get(field)
    elif language == 'de':
        return de_dict.get(field)
    elif language == 'fr':
        return fr_dict.get(field)
    elif language == 'pt':
        return pt_dict.get(field)
    else:
        return en_dict.get(field)


def lang_to_dict(language):
    """
    Convert a specific .txt lang file into key-values
    :param language: Language code name (iso 639-1)
    :return: dict
    """
    file = open('lang/'+language+'.txt', 'r')
    dictionary = {}
    for line in file.readlines():
        args = line.split(':')
        key = args[0].strip()
        value = args[1].strip()
        dictionary.update({key: value})

    return dictionary


def handle_spanish(message):
    """
    Dame (qty) cursos de (topic)
    :param message:
    :return: quantity, topic
    """
    try:

        fixed_message = message.replace('acerca de', 'de')
        fixed_message = fixed_message.replace('sobre', 'de')

        elements = fixed_message.split(' ')
        quantity = elements[1]

        numbers = ['un', 'dos', 'tres']

        try:
            if len(quantity) >= 2:
                quantity = numbers.index(quantity) + 1
            else:
                quantity = int(quantity)
        except ValueError:
            quantity = 1

        if quantity == 0:
            quantity += 1

        quantity = min(quantity, 3)

        topic = elements[elements.index('de') + 1:]
        topic = ' '.join(topic)
        topic = topic.strip()

        return quantity, topic

    except ValueError:

        return 0, None


def handle_english(message):
    """
        Give me (qty) courses about (topic)
        :param message:
        :return: quantity, topic
        """
    try:

        message = message.replace('courses', 'course')

        elements = message.split(' ')
        quantity = elements[2]
        numbers = ['one', 'two', 'three']
        try:
            if (quantity == 'a') or (quantity == 'an'):
                quantity = 1
            elif len(quantity) >= 3:
                quantity = numbers.index(quantity) + 1
            else:
                quantity = int(quantity)
        except ValueError:
            quantity = 1

        if quantity == 0:
            quantity += 1

        quantity = min(quantity, 3)

        print(elements[5:])
        topic = ' '.join(elements[5:])
        return quantity, topic

    except ValueError:

        return 0, None


def handle_german(message):
    """
    Gibt mir (qty) Kurs uber (topic)
    :param message:
    :return: quantity, topic
    """
    try:

        fixed_message = message.replace('über', 'uber')
        fixed_message = fixed_message.replace('auf', 'uber')
        elements = fixed_message.split(' ')
        quantity = elements[2]
        numbers = ['ein', 'zwei', 'drei']
        try:
            if len(quantity) >= 3:
                quantity = numbers.index(quantity) + 1
            else:
                quantity = int(quantity)

        except ValueError:
            print('Value error in German: Assigning 1')
            quantity = 1

        if quantity == 0:
            quantity += 1

        quantity = min(quantity, 3)

        topic = elements[elements.index('uber') + 1:]
        topic = ' '.join(topic)

        return quantity, topic

    except ValueError:

        return 0, None


def handle_french(message):
    """
    Donnez moi (qty) cours (topic)
    :param message:
    :return: quantity, topic
    """
    try:
        fixed_message = message.replace('donnez moi', 'donnez-moi')
        elements = fixed_message.split(' ')
        quantity = elements[1]
        numbers = ['un', 'deux', 'trois']
        try:
            if (quantity == 'un') or (len(quantity) >= 3):
                quantity = numbers.index(quantity) + 1
            else:
                quantity = int(quantity)

        except ValueError:
            quantity = 1

        if quantity == 0:
            quantity += 1

        quantity = min(quantity, 3)

        topic = elements[elements.index('cours') + 1:]
        topic = ' '.join(topic)
        topic = topic.strip()

        return quantity, topic

    except ValueError:
        return 0, None


def handle_portuguese(message):
    """
        Dê-me (qty) cursos de (topic)
        :param message:
        :return: quantity, topic
        """

    try:

        fixed_message = message.replace('-', '')
        fixed_message = fixed_message.replace('do', 'de')
        elements = fixed_message.split(' ')
        quantity = elements[1]
        numbers = ['um', 'dois', 'tres']
        try:
            if (quantity == 'um') or (len(quantity) >= 3):
                quantity = numbers.index(quantity) + 1
            else:
                quantity = int(quantity)
        except ValueError:
            quantity = 1

        if quantity == 0:
            quantity += 1

        quantity = min(quantity, 3)

        topic = elements[elements.index('de') + 1:]
        topic = ' '.join(topic)
        topic = topic.strip()

        return quantity, topic

    except ValueError:

        return 0, None


# Load every supported language dictionary
es_dict = lang_to_dict('es')
en_dict = lang_to_dict('en')
de_dict = lang_to_dict('de')
fr_dict = lang_to_dict('fr')
pt_dict = lang_to_dict('pt')


