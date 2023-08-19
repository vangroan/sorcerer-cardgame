from argparse import ArgumentParser, Namespace

from sorcerer import client


def parse_args() -> Namespace:
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")
    hello_cmd = subparsers.add_parser("hello")
    hello_forever_cmd = subparsers.add_parser("hello-forever")

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "hello":
        client.hello()
    elif args.command == "hello-forever":
        client.hello_forever()


if __name__ == "__main__":
    main()
