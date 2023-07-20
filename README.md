# image-retrieval-playground
A repo with code for similar images search and removal.

## Installation
It's recommended to use a virtual env and python >=3.10.6. To install dependencies run the following command:
```bash
pip install -r requirements.txt
```

## Usage
Firstly you need to split your images into per-camera folders using the following script:
```bash
./scripts/split_per_camera.py <path_to_images_dir>
```

Then you can start filtering images with the `./scripts/filter_images.py` script.
Use with `--help` to obtain the information about arguments.


## Questions answering
### What did you learn after looking on our dataset?
The dataset consists of png images (without exif data) of parking from 4 cameras. For some reason images from a single camera can have different resolution (most probably it was done manually). Also it can contain corrupted images (`c21_2021_03_27__10_36_36.png`, `c21_2021_03_27__12_53_37.png`). Looks like frames are grabbed each ~173 seconds (about 500 images per day) but for some reason we can skip frames.

Based on dataset analysis I would say that images from different cameras don't need to be compared with each other.


### How does you program work?
Firstly the dataset was splitted into per-camera folders with `scripts/split_per_camera.py` script. After that the `scripts/filter_images.py` was executed for each camera dir. It works as follows:
1. Parse and check args.
2. Create a subdirectory inside the source directory for removed images.
3. Sort images by their name.
4. Iterate over the images to compare each with each (O(n^2)).
   1. Check that read image meets some minimal requirements.
   2. Resize the image to the provided shape.
   3. Preprocess image using provided function.
5. If we decided that comparing images are similar - move the image from outer loop to the folder for removed images.
6. Calculated by `compare_frames_change_detection` score reflects an approximate number of changed pixels. To remove the dependency from image size the score is converted to relative.


### What values did you decide to use for input parameters and how did you find these values?
* The `--resize-to` was picked for each camera separately to keep the aspect ratio. A smaller size was chosen to reduce the number of computations.
* The `--black-mask` also was picked for each camera separately. The idea was to remove static area (like the ceiling) and cut borders from each side to avoid small changes on image boundaries.
* The `--blur-radius` was set not to high just to suppress a little bit a noice from camera.
* Also the default value for `--th` is set to `0.025` because it should be a value for approximately a half of distant car.
* The `--min-diff-area` with default value `0.005` uses similar logic but for pedestrians.

Here the full list of executed commands:
```bash
./filter_images.py ./camera_10/ --resize-to 480 640 --black-mask 5 14 5 10 --blur-radius 3
./filter_images.py ./camera_20/ --resize-to 540 960 --black-mask 22 29 5 5 --blur-radius 3
./filter_images.py ./camera_21/ --resize-to 540 960 --black-mask 10 30 5 5 --blur-radius 3
./filter_images.py ./camera_23/ --resize-to 540 960 --black-mask 5 31 5 5 --blur-radius 3
```

### What you would suggest to implement to improve data collection of unique cases in future?
We can try to save frames from camera only with motion. It can be done with H.264 encoder. It calculates motion vectors while generating compressed video. Using these vectors can we threshold them by their strength. If more than N vectors thresholded - mark the current frame as containing motion. This idea is also implemented here: https://github.com/resolator/rpi-surveillance

Another idea more complicated and can be implemented in case of each camera is a part of an embedded device. Launch a simple feature extractor (frame rate is a hyperparam) and extract features for each frame. Compare with vectors of already collected frames. If it has a higher than N distance to the closest in the database - save it and add to the database the calculated feature vector (face re identification approach).

### Any other comments about your solution?
In general my solution is not perfect and can be improved depending on what is the purpose of the dataset which we are collecting. I was trying to develop an algorithm based on a consideration that we collecting the to train object detection model.

Here some other comments:
1. Cut image instead of masking in `preprocess_image_change_detection()` draw_color_mask -> mask_borders (done in my solution).
2. Move `mask_borders(gray, black_mask)` to the top of function to speed-up it in case of Gaussian blur (done in my solution).
3. Get rid of imutils. We use only a single function from this package that is not hard to implement by ourself.
4. cv2.cvtColor already returns a copy of the image so we don't need a copy in `preprocess_image_change_detection` (done in my solution).
5. cv2.findContours doesn't modifies the source image so we don't need a copy in `compare_frames_change_detection` (done in my solution).
6. In case of much larger datasets we can also perform per-halfday splitting. In this case we can optimize the comparison loop by introducing a sliding window over the time with a size like 1 hour. Also based on the estimation 500 frames per day it is possible to keep all images in memory. With this proposal we also can introduce a multiprocessing.
