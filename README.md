# Sofa


This is a minimalist tool for removing faces from a video, and removing clips
which the algorithm wasn't succesfull


<p align="center">
  <img src="doc/static/img/tofu.png">
</p>


## Installation

### Windows 10

#### Requirements

You should install the following packages before installing the **DEV** version or the **Bin** version:

* Install <a href="https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe">Python 3.6</a>;
* Install <a href="https://codecguide.com/download_kl.htm">k-lite codecs</a>;
* Install <a href="https://www.microsoft.com/pt-br/download/details.aspx?id=52685">Visual C++ 2015</a>.


> When installing Python, remember to checkout the box for adding it to your `PATH`.


#### DEV version

* Download <a href="https://github.com/smartops-project/sofa/archive/master.zip">master.zip</a>;
* unzip it;
* run install.bat;
* run sofa.bat.

### Ubuntu

#### DEV version

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
