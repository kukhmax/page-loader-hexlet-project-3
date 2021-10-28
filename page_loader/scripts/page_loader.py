import argparse
from page_loader.engine import download, WD
import requests
import logging.config
import logging
from page_loader.settings_log import logger_config

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
        download(
            args.url,
            args.output
        )
    except requests.exceptions.Timeout:
            logger.error(" Very Slow Internet Connection.")
            print("Very Slow Internet Connection.")
    except requests.exceptions.ConnectionError:
            logger.error(" Network Unavailable. Check your connection.")
            print("Network Unavailable. Check your connection.")
    except requests.exceptions.MissingSchema:
            logger.error(" 503 Service Unavailable. Retrying download ... ")
            print("503 Service Unavailable. Retrying download ...")
    else:
        logger.debug(f'download({args.url}) run')


if __name__ == '__main__':
    main()
