#! /usr/bin/env python
#
# This file is part of khmer, http://github.com/ged-lab/khmer/, and is
# Copyright (C) Michigan State University, 2009-2014. It is licensed under
# the three-clause BSD license; see doc/LICENSE.txt.
# Contact: khmer-project@idyll.org
#
"""
Find highly-connected k-mers and output them in a .stoptags file, for use
in partitioning.

% python scripts/find-knots.py <base>
"""

import argparse
import glob
import os

import khmer
from khmer.file import check_file_status, check_space

# counting hash parameters.
DEFAULT_COUNTING_HT_SIZE = 3e6                # number of bytes
DEFAULT_COUNTING_HT_N = 4                     # number of counting hash tables

# Lump removal parameters.  Probably shouldn't be changed, but who knows?
#
# explanation:
#
# We will walk EXCURSION_DISTANCE out from each tag; if we find more than
# EXCURSION_KMER_THRESHOLD kmers within that range, this will be a "big"
# excursion and we will track all k-mers visited.  If we find that any
# k-mer has been visited more than EXCURSION_KMER_COUNT_THRESHOLD times,
# we will mark it as BAD and make it a stop tag for traversal.

# don't change these!
EXCURSION_DISTANCE = 40
EXCURSION_KMER_THRESHOLD = 200
EXCURSION_KMER_COUNT_THRESHOLD = 2
# EXCURSION_KMER_COUNT_THRESHOLD=5 # -- works ok for non-diginormed data

#


def main():
    parser = argparse.ArgumentParser(
        description="Find all highly connected k-mers.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--n_hashes', '-N', type=int, dest='n_hashes',
                        default=DEFAULT_COUNTING_HT_N,
                        help='number of counting hash tables to use')
    parser.add_argument('--hashsize', '-x', type=float, dest='min_hashsize',
                        default=DEFAULT_COUNTING_HT_SIZE,
                        help='lower bound on counting hashsize to use')
    parser.add_argument('graphbase')

    args = parser.parse_args()

    graphbase = args.graphbase

    # @RamRS: This might need some more work
    infiles = [graphbase + '.ht', graphbase + '.tagset']
    if os.path.exists(graphbase + '.stoptags'):
        infiles.append(graphbase + '.stoptags')
    for _ in infiles:
        check_file_status(_)

    check_space(infiles)

    print 'loading ht %s.ht' % graphbase
    htable = khmer.load_hashbits(graphbase + '.ht')

    print 'loading tagset %s.tagset...' % graphbase
    htable.load_tagset(graphbase + '.tagset')

    initial_stoptags = False    # @CTB regularize with make-initial
    if os.path.exists(graphbase + '.stoptags'):
        print 'loading stoptags %s.stoptags' % graphbase
        htable.load_stop_tags(graphbase + '.stoptags')
        initial_stoptags = True

    pmap_files = glob.glob(args.graphbase + '.subset.*.pmap')

    print 'loading %d pmap files (first one: %s)' % (len(pmap_files),
                                                     pmap_files[0])
    print '---'
    print 'output stoptags will be in', graphbase + '.stoptags'
    if initial_stoptags:
        print '(these output stoptags will include the already-loaded set)'
    print '---'

    # create counting hash
    ksize = htable.ksize()
    counting = khmer.new_counting_hash(ksize, args.min_hashsize, args.n_hashes)

    # load & merge
    for index, subset_file in enumerate(pmap_files):
        print '<-', subset_file
        subset = htable.load_subset_partitionmap(subset_file)

        print '** repartitioning subset... %s' % subset_file
        htable.repartition_largest_partition(subset, counting,
                                             EXCURSION_DISTANCE,
                                             EXCURSION_KMER_THRESHOLD,
                                             EXCURSION_KMER_COUNT_THRESHOLD)

        print '** merging subset... %s' % subset_file
        htable.merge_subset(subset)

        print '** repartitioning, round 2... %s' % subset_file
        size = htable.repartition_largest_partition
        (None, counting, EXCURSION_DISTANCE, EXCURSION_KMER_THRESHOLD,
         EXCURSION_KMER_COUNT_THRESHOLD)

        print '** repartitioned size:', size

        print 'saving stoptags binary'
        htable.save_stop_tags(graphbase + '.stoptags')
        os.rename(subset_file, subset_file + '.processed')
        print '(%d of %d)\n' % (index, len(pmap_files))

    print 'done!'

if __name__ == '__main__':
    main()
