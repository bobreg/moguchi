import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

MOGUCHI_LOG_FOLDER = 'moguchi_log'
MOGUCHI_LOG_FILE = 'm_log.log'

class Moguchi_log:
	def __init__(self) -> None:
		self.m_logPath = Path(str(Path.home()) + '/' + MOGUCHI_LOG_FOLDER)
		self.m_logPath.mkdir(parents=True, exist_ok=True)
		self.logger = logging.getLogger('moguchi_log')
		self.logger.setLevel(logging.INFO)
		self.logger.propagate = False

		if not self.logger.handlers:
			log_handler = RotatingFileHandler(str(self.m_logPath) + '/' + MOGUCHI_LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
			format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
			log_handler.setFormatter(format)
			self.logger.addHandler(log_handler)

	def msg_info(self, log_msg: str):
		self.logger.info(log_msg)

	def msg_warn(self, log_msg: str):
			self.logger.warning(log_msg)

	def msg_error(self, log_msg: str):
			self.logger.error(log_msg)

