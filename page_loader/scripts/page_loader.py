import argparse
from page_loader.engine import download, WD, AppError
import logging.config
import logging
from page_loader.settings_log import logger_config
import sys

logging.config.dictConfig(logger_config)

logger = logging.getLogger('app_logger')


def main():
    # positional arguments
    parser = argparse.ArgumentParser(description='Page loader')
    parser.add_argument('url', type=str)

    # optional arguments
    parser.add_argument(
        '-o', '--output',
        default=WD,
        help='output dir (default: working dir)'
    )
    args = parser.parse_args()

    try:
        file_path = download(
            args.url,
            args.output
        )
    except AppError as e:
        logger.error(e)
        print(e)
        sys.exit(1)
    except Exception as e:
        logger.error(f'Unknown error: {e}')
        sys.exit(1)
    else:
        # logger.debug(f'download({args.url}) run')
        print(f"\x1b[3m\x1b[32mPage was successfuly \
downloaded into '{file_path}'\x1b[0m\x1b[37m")
        sys.exit(0)


if __name__ == '__main__':
    main()
