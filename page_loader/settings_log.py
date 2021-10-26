import logging


class MegsHandler(logging.Handler):
    def __init__(self, filename):
        logging.Handler.__init__(self)
        self.filename = filename

    def emit(self, record):
        message = self.format(record)
        with open(self.filename, 'a') as file:
            file.write(message + '\n')


logger_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'std_format': {
            'format': '{asctime} :: {levelname} :: {module}:{funcName}:{lineno} :: {name} :: {message}',  # noqa E501
            'style': '{'
        }
    },
    'handlers': {
        'file': {
            '()': MegsHandler,
            'level': 'DEBUG',
            'filename': 'debug.log',
            'formatter': 'std_format'
        }
    },
    'loggers': {
        'app_logger': {
            'level': 'DEBUG',
            'handlers': ['file']
        }
    }
}
