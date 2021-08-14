# ytdownloader_GUI

A simple YouTube downloader written in Python with a GUI.

## Installation

Run the following commands:

```
python -m pip install git+https://github.com/pytube/pytube
git clone https://github.com/sgrontflix/ytdownloader_GUI
cd ytdownloader_GUI
```

or 

```
python3 -m pip install git+https://github.com/pytube/pytube
git clone https://github.com/sgrontflix/ytdownloader_GUI
cd ytdownloader_GUI
```

And get [FFmpeg](https://ffmpeg.org/download.html).

### For Windows users

Make sure to install [Python](https://www.python.org/downloads/) and [Git](https://gitforwindows.org/) before executing the commands above and downloading FFmpeg.

Check `Add Python to environment variables` in `Advanced Options` when installing Python.

You can leave everything on default when installing Git.

After downloading an FFmpeg Windows build from the official website or directly from [here](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z), unpack the archive and put the extracted folder inside `ytdownloader_GUI`. Your **FFmpeg path** will be `<NAME_OF_EXTRACTED_FOLDER>\bin\ffmpeg.exe`.

### For Linux users

You can install everything you need from the command line.

After installing FFmpeg, run `whereis ffmpeg` to get the full installation path. It should be something like `/usr/bin/ffmpeg`.

## Usage

`python main.py`

or

`python3 main.py`

## Issues

If you encounter any issue, try upgrading your pytube release by running the following command:

`python -m pip install git+https://github.com/pytube/pytube --upgrade`

or

`python3 -m pip install git+https://github.com/pytube/pytube --upgrade`

If upgrading pytube doesn't fix your problem, try updating this project by running the following command inside the `ytdownloader_GUI` folder:

`git pull origin main`

If the script still doesn't work, please let me know by [creating an issue](https://github.com/sgrontflix/ytdownloader_GUI/issues/new).
