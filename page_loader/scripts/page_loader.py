import argparse
from page_loader.engine import download, CWD


def main():
    # positional arguments
    parser = argparse.ArgumentParser(description='Page loader')
    parser.add_argument('url', type=str)

    # optional arguments
    parser.add_argument(
        '-o', '--output',
        default=CWD,
        help='set path to dir (default: cwd)'
    )
    args = parser.parse_args()

    print(download(
        args.url,
        args.output
    ))


if __name__ == '__main__':
    main()
