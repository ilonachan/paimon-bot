import runpy
import os.path
import yaml
import logging.config
from discord.utils import get
import psutil
from psutil import TimeoutExpired

#
# Logger Configuration
#
with open('logging.yaml', 'r') as lf:
    log_cfg = yaml.safe_load(lf.read())
logging.config.dictConfig(log_cfg)

log = logging.getLogger(__name__)


class PidTracker:
    def __init__(self, path='./pid.lock'):
        self.path = path

    def __enter__(self):
        if os.path.exists(self.path):
            log.info('The process is already running, terminating')
            with open(self.path, 'r') as f:
                pid = int(f.readline())
                proc: psutil.Process = get(psutil.process_iter(), pid=pid)
                if proc is not None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except TimeoutExpired:
                        if proc.is_running():
                            proc.kill()

        pid = str(os.getpid())
        with open(self.path, 'w') as f:
            f.write(pid)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.path.exists(self.path):
            os.remove(self.path)
        else:
            log.warning('No lock file was found for this process')


if __name__ == '__main__':
    with PidTracker():
        runpy.run_module(mod_name='paimon', run_name='paimon')
