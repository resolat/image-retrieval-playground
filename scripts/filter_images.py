#!/usr/bin/env python3
"""Iterate over given directory of png images and find all similar (O(n^2))."""
import argparse
import numpy as np
from tqdm import tqdm
from shutil import move
from pathlib import Path

import utils


def parse_args():
    """Argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('src_dir', type=Path,
                        help='A path to a source directory with images.')
    parser.add_argument('--resize-to', type=int, nargs=2,
                        help='Resize all images to the given H and W.')
    parser.add_argument('--th', type=float, default=0.025,
                        help='A threshold ratio for image difference. '
                             'Should be in range [0; 1].')
    parser.add_argument('--black-mask', type=int, nargs=4,
                        default=(5, 10, 5, 0),
                        help='Mask boundaries of comparing images '
                             '(right, top, left, bottom percentage).')
    parser.add_argument('--min-diff-area', type=float, default=0.005,
                        help='Minimum ratio of pixels to take into account '
                             'changed area.')
    parser.add_argument('--blur-radius', type=int, nargs='+',
                        help='Blur radiuses for preprocessing. Must be odd.')

    return parser.parse_args()


def check_args(args):
    if args.blur_radius is not None:
        for x in args.blur_radius:
            assert x % 2 == 1, '--blur-radius must be odd.'

    assert 0 <= args.th <= 1, '--th should be in range [0; 1].'
    assert 0 <= args.min_diff_area <= 1, \
        '--min-diff-area should be in range [0; 1].'


def move_to_deleted(img_path, del_dir):
    move(img_path, del_dir / img_path.name)


def main(args):
    """Application entry point."""
    # args checking
    check_args(args)

    # create an axillary directory for deleted images
    dst_dir = args.src_dir / 'for_deletion'
    dst_dir.mkdir(exist_ok=True)

    # collect paths for deletion
    paths = sorted(list(args.src_dir.glob('*.png')))
    idx = 0
    pbar = tqdm(total=len(paths), desc='Comparing')
    while idx < len(paths):
        pbar.update(1)
        img_1 = utils.read_preproc_img(
            paths[idx], args.resize_to, args.blur_radius, args.black_mask)

        if img_1 is None:
            print(f'Warning: moving {paths[idx]} because it didn\'t '
                  f'meet minimal requirements.')
            move_to_deleted(paths.pop(idx), dst_dir)
            continue

        jdx = idx + 1
        pixels_num = np.prod(img_1.shape[:2])
        while jdx < len(paths):
            img_2 = utils.read_preproc_img(
                paths[jdx], args.resize_to, args.blur_radius, args.black_mask)
            if img_2 is None:
                print(f'Warning: moving {paths[jdx]} because it didn\'t '
                      f'meet minimal requirements.')
                move_to_deleted(paths.pop(jdx), dst_dir)
                continue

            # score is a percentage of changed area compared to non-masked area
            score = utils.compare_frames_change_detection(
                img_1, img_2, int(pixels_num * args.min_diff_area))[0]
            score = score / pixels_num

            if score < args.th:
                move_to_deleted(paths.pop(idx), dst_dir)
                idx -= 1  # will be incremented back at the end of the top loop
                break

            jdx += 1
        idx += 1
    pbar.close()
    print(f'Done. Deleted images are moved to {dst_dir}.')


if __name__ == '__main__':
    args = parse_args()
    main(args)
