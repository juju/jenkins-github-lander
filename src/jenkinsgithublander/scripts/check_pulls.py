import argparse
from ConfigParser import ConfigParser
from os import path

from jenkinsgithublander import VERSION
from jenkinsgithublander.jobs import kick_mergeable_pull_requests
from jenkinsgithublander.utils import build_config


def parse_args():
    """Handle building what we want to do based on the arguments.

    Examples:
        check_pulls.py --version
        check_pulls.py --ini development.ini

    """
    desc = """Check for pull requests ready for building and merging.

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

    settings = dict(cfg.items('app:main', raw=True))
    return build_config(settings)


def run(args, config):
    kicked = kick_mergeable_pull_requests(config)
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
