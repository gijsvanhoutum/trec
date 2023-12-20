# TREC: A threaded video player and recorder 

**TREC** is a GUI application for video recording and playing.

## Main Features / Comments
Major information:

  - 4 Threads; GUI, Display, Recording, Data acquisition for speed.
  - Multiple resolutions and frame rates through Video4Linux integration
  - Easy to expand for new devices i.e. Dinolite-edge etc.
  - Build with Python,Qt, OpenCV and Numpy
  - Live information in about Frame-rate and frame-rate capacity (%) 

## Dependencies
Video4Linux device drivers are needed. To check run in terminal:
```sh
v4l2-ctl
```
If the package is not installed, install it with:
```sh
sudo apt install v4l-utils
```
After installation the visible devices can be checked with:
```sh
v4l2-ctl --list-devices
```

## How to get it

Git is assumed to be installed. Clone the repository to current working directory
```sh
git clone https://github.com/gijsvanhoutum/VSI_recorder.git
```

