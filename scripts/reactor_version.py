app_title = "ReActor"
version_flag = "v0.6.1-b2"

from scripts.reactor_logger import logger, get_Run, set_Run
from scripts.reactor_globals import DEVICE

is_run = get_Run()

if not is_run:
    logger.status(f"Running {version_flag} on Device: {DEVICE}")
    set_Run(True)
