import argparse
from ConfigParser import ConfigParser
from os import path

from jenkinsgithublander import VERSION
from jenkinsgithublander.jobs import merge_pull_requests


def parse_args():
    """Handle building what we want to do based on the arguments.

    Examples:
        api.py invites list
        api.py invites set -u username -c 10
        api.py accounts list --inactive
        api.py readable list --todo

    """
    desc = """Command line client for the Bookie bookmark service.

    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        '--version',
        action='version',
        version=VERSION)

    parser.add_argument(
        '-i', '--ini',
        action='store',
        required=True,
        help='Path to the ini file containing the jenkins and github config.'
    )

    return parser.parse_args()


def parse_config(ini):

    if not path.exists(ini):
        raise Exception('Ini file not found: ' + ini)

    cfg = ConfigParser()
    cfg.readfp(open(ini))

    return dict(cfg.items('app:main', raw=True))


def run(args, config):
    kicked = merge_pull_requests(config)
    if kicked:
        ret = "\n".join(kicked)
    else:
        ret = "No pull requests to merge."

    print ret


def main():
    args = parse_args()
    cfg = parse_config(args.ini)
    run(args, cfg)


if __name__ == "__main__":
    main()
