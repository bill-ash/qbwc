import os
import time
from pathlib import Path

path = Path().absolute()
print(path)
time.sleep(3)
os.environ["DJANGO_SETTINGS_MODULE"] = "test_settings"
