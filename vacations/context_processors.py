import datetime


def load_vacations_global_context(request):
    DEFAULT = 0
    VIEW = 1
    EDIT = 2

    ARCHIVE = 0
    RELEVANT = 1
    PLANNED = 2

    relevant_years = []
    for i in range(4):
        relevant_years.append(int(datetime.date.today().year - i + 1))

    return {'relevant_years': relevant_years, 'DEFAULT': DEFAULT, 'VIEW': VIEW, 'EDIT': EDIT, 'ARCHIVE': ARCHIVE, 'RELEVANT': RELEVANT, 'PLANNED': PLANNED}
