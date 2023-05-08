import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def parse_time_stamp(x):
    try:
        return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z")
    except Exception as e:
        logger.error("Error parsing time stamp")
        return datetime.utcnow()
