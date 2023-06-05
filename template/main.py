import threading
import os
from sgo.control import Control


def run_control():
    Control().run()


def main():
    os.environ.setdefault('SGO_PROJECT_SETTINGS', 'template.settings')
    control_thread = threading.Thread(target=run_control)
    control_thread.start()
    Control().shell()


if __name__ == '__main__':
    main()
