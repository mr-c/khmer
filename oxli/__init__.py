#!/usr/bin/env python
#
# This file is a part of khmer, http://github.com/ged-lab/khmer/, and is
# Copyright (C) Michigan State University, 2015. It is licensed under the
# three-clause BSD license; see doc/LICENSE.txt.
# Contact: khmer-project@idyll.org
#

"""
Single entry point script for khmer
"""

import argparse
import textwrap
from oxli import build_graph, common


def get_parser():
    """
    returns the parser object for the oxli subcommand handler
    """

    parser = argparse.ArgumentParser(
        description='Single entry point script for khmer',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers()

    # build-graph (formerly load-graph) parsers here
    parser_build_graph = \
            subparsers.add_parser('build_graph',
                help="Load sequences into the compressible graph format plus "
                "optional tagset",
                description="Load sequences into the compressible graph format"
                "plus optional tagset")

    common.add_hashbits_args(parser_build_graph)
    build_graph.add_args(parser_build_graph)
    parser_build_graph.set_defaults(func=execute_build_graph)

    return parser

def execute_build_graph(args):
    build_graph.main(args)
    

def main():
    """
    main function; does the parsing and kicks off the subcommand
    """
    args = get_parser().parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
