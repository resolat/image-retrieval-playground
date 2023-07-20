#!/usr/bin/env python3
"""
Create directories with camera_id names in source directory and move images
into the corresponding folder.
"""
import argparse
from tqdm import tqdm
from shutil import move
from pathlib import Path
from datetime import datetime as dtm


def parse_args():
    """Argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('src_dir', type=Path,
                        help='A path to a source directory with images.')

    return parser.parse_args()


def parse_timestamp(ts_str):
    """Parse a timestamp from 1689871397000 to 2021_06_16__21_18_18 format."""
    return dtm.fromtimestamp(int(ts_str) / 1000).strftime('%Y_%m_%d__%H_%M_%S')


def main(args):
    """Application entry point."""
    for img_path in tqdm(args.src_dir.glob('*.png'), desc='Splitting'):
        # parse camera ID
        camera_id = img_path.stem.replace('-', '_').split('_')[0][1:]

        # prepare dst name
        dst_img_name = img_path.name
        splitted = img_path.stem.split('-')
        if len(splitted) == 2:
            # convert the timestamp to the common format
            ts = parse_timestamp(splitted[1])
            dst_img_name = f'c{camera_id}_{ts}{img_path.suffix}'

        # create a destitanion directory and move the image
        dst_dir = img_path.parent / ('camera_' + camera_id)
        dst_dir.mkdir(exist_ok=True)
        move(img_path, dst_dir / dst_img_name)

    print('Done.')


if __name__ == '__main__':
    args = parse_args()
    main(args)
