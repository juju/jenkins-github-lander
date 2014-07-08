"""Update the pull request given the results of the merge jenkins job.

  default:   then merge the pull request via the api.
  --failure: then comment on the pull request with information about the
             failure.

"""
import argparse
from ConfigParser import ConfigParser
from os import path
from textwrap import dedent
import sys

from jenkinsgithublander import (
    LanderError,
    VERSION,
)
from jenkinsgithublander.jobs import (
    mark_pull_request_build_failed,
    do_merge_pull_request
)
from jenkinsgithublander.utils import build_config


def parse_args():
    """Handle building what we want to do based on the arguments.

    Examples:
        lander-merge-result --version
        lander-merge-result --ini development.ini --pr=5 --build=25
        lander-merge-result --ini development.ini \
                            --failure="Build failed" --pr=5 --build=25

    """
    desc = """Give a pull request, merge it or comment on the failure in case
    of a failing build.

    """
    parser = argparse.ArgumentParser(description=dedent(desc))
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

    parser.add_argument(
        '-p', '--pr',
        action='store',
        required=True,
        help='The Github pull request that was tested.'
    )

    parser.add_argument(
        '-j', '--job-name',
        action='store',
        dest='job_name',
        required=True,
        help='The Github pull request that was tested.'
    )

    parser.add_argument(
        '--build-number',
        action='store',
        dest='build_number',
        required=True,
        help='The Jenkins build number this result is for.'
    )

    parser.add_argument(
        '--failure',
        action='store',
        default=None,
        help='A message indicating the build has failed.'
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
    if args.failure is not None:
        ret = mark_pull_request_build_failed(
            args.job_name, args.pr, args.build_number, args.failure, config)
    else:
        ret = do_merge_pull_request(
            args.job_name, args.pr, args.build_number, config)

    print ret


def main():
    args = parse_args()
    cfg = parse_config(args.ini)
    try:
        run(args, cfg)
    except LanderError as e:
        sys.stderr.write("ERROR: {}\n".format(e))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
