from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_NAME = BASE_DIR.name

PROCESS_COUNT = 1
THREAD_COUNT = 1

MODELS = f'{PROJECT_NAME}.models'

DATABASE_USE = 'DEFAULT'

DATABASE = {
    "DEFAULT": {
        "ENGINE": "mysql",
        'DB': 'sgo_demo',
        'USER': 'root',
        'PWD': '2001',
        'HOST': '127.0.0.1',
        'PORT': 3306,
    },
}

# Test
if __name__ == '__main__':
    print(MODELS)
