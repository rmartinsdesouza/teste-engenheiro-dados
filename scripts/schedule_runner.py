import runpy
import schedule
import time
from pathlib import Path


def job():
    runpy.run_path(str(Path(__file__).with_name("clientes_raw.py")), run_name="__main__")


if __name__ == "__main__":
    schedule.every().day.at("05:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
