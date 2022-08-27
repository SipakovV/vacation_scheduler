
def load_permission_codes(request):
    DEFAULT = 0
    VIEW = 1
    EDIT = 2

    ARCHIVE = 0
    RELEVANT = 1
    PLANNED = 2

    return {'DEFAULT': DEFAULT, 'VIEW': VIEW, 'EDIT': EDIT, 'ARCHIVE': ARCHIVE, 'RELEVANT': RELEVANT, 'PLANNED': PLANNED}