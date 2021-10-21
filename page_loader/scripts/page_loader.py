import argparse
from page_loader.engine import download, PWD


def main():
    # positional arguments
    parser = argparse.ArgumentParser(description='Page loader')
    parser.add_argument('url', type=str)

    # optional arguments
    parser.add_argument(
        '-o', '--output',
        default=PWD,
        help='output dir (default: working dir)'
    )
    args = parser.parse_args()

    print(download(
        args.url,
        args.output
    ))


if __name__ == '__main__':
    main()
