import argparse
from page_loader.engine import download, WD


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

    path_to_html_file = download(
        args.url,
        args.output
    )
    print(path_to_html_file)


if __name__ == '__main__':
    main()
