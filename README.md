# Sofa

This is a minimalist tool for removing faces from a video, and removing clips
which the algorithm wasn't succesfull

<p align="center">
  <img src="doc/static/img/tofu.png">
</p>


## Installation

### Windows 10

#### Requirements

* Install <a href="https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe">Python 3.6</a>;
* Install <a href="https://codecguide.com/download_kl.htm">k-lite codecs</a>.


#### Dev version

* Download <a href="https://github.com/smartops-project/sofa/archive/master.zip">master.zip</a>;
* unzip it;
* run install.bat;
* run sofa.bat.

#### Release

* Download <a href="https://drive.google.com/drive/folders/1iG3_ZRW80emiX2nW6Gm-G3elYRg-bbkm?usp=sharing">install_sofa.zip</a>;
* unzip it;
* run `sofaSetup.exe`.

### Ubuntu

#### Dev version

If you are planning to play *MP4* or any other proprietary formats, you need
to install the following packages:

``` bash
$ sudo apt install ubuntu-restricted-extras
$ sudo apt install build-essential qt5-default
$ sudo apt install libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio
```

Then, install the required Python Libraries.
It is recommended to create a virtual environment for the application, instead
of installing it globally:

```bash
$ cd <project_dir>
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -U pip
$ pip install -r requirements.txt
```
