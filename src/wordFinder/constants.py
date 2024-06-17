MODULES_PATH = r'C:\Users\tomtom\Documents\travail_dev\local_lhorda_tools'

EXCLUDED_DIRECTORIES = ('__pycache__', '.idea', '.git', 'docs', '.gitignore')

EXCLUDED_MODULES = ('__init__.py',)

EXCLUDED_CHARACTERS = (r"""/""", r"#",)

SEARCH_PATH = '__search_path__'
DEV_MODE = '__dev_mode__'
COLUMN_COUNT = '__column_layout__'
LOCAL_CHECKED_MODULES = '__local_checked_modules__'
GIT_HUB_CHECKED_MODULES = '__gitHub_checked_modules__'
GIT_HUB_HEY = '__git_hub_key__'

DEFAULT_CONFIG = {
    SEARCH_PATH: "",
    DEV_MODE: False,
    COLUMN_COUNT: 5,
    LOCAL_CHECKED_MODULES: [],
    GIT_HUB_CHECKED_MODULES: [],
    GIT_HUB_HEY: '',
}

