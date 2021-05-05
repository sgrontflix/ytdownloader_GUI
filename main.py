from utilities import *
from gui_classes import *
from tkinter import messagebox
from threading import Thread
from pathlib import Path
from pytube import YouTube
import sys
import subprocess


def handle_download():
    """
    Handles the audio/video download by disabling all the input fields,
    starting the actual download thread and calling the thread monitoring function

    :return: None
    """
    yt_url.config(state='disabled')
    ffmpeg_path.config(state='disabled')
    gpu_checkbox.config(state='disabled')
    audio_only_checkbox.config(state='disabled')
    download_button.config(state='disabled')

    dl = Thread(target=execute_download)
    dl.start()

    monitor_download(dl)


def monitor_download(thread):
    """
    Checks every 100ms whether the given thread is still alive or not.
    If the thread is no longer running, it enables back all input fields.
    This function is required because if the thread terminates
    unexpectedly, all input fields will stay disabled

    :param thread: Thread to be monitored
    :return: None
    """
    if thread.is_alive():
        root.after(100, lambda: monitor_download(thread))
    else:
        download_button.config(state='normal')
        audio_only_checkbox.config(state='normal')
        gpu_checkbox.config(state='normal')
        ffmpeg_path.config(state='normal')
        yt_url.config(state='normal')


def execute_download():
    """
    Carries out the actual download and merging of the tracks

    :return: None
    """

    # clear the previous output before downloading the new file
    #
    # text indices work differently from entry indices
    # https://tkdocs.com/shipman/text-index.html
    console_output.config(state='normal')
    console_output.delete(1.0, tk.END)
    console_output.config(state='disabled')

    enable_gpu = ' -hwaccel cuda -hwaccel_output_format cuda'
    merge_command = ffmpeg_path.get() + ' -y' + (enable_gpu if gpu.get() else '') + \
        ' -hide_banner -loglevel panic -i video.mp4 -i audio.mp4 -c:v copy -c:a copy'

    if not youtube_url_validation(yt_url.get()):
        messagebox.showerror('ERROR', 'Invalid URL detected')
        return

    ffmpeg_executable = Path(ffmpeg_path.get())
    if not ffmpeg_executable.is_file():
        messagebox.showerror('ERROR', 'Invalid path detected')
        return

    # get yt link info
    yt = YouTube(yt_url.get())

    audio_track = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('bitrate')[-1]

    if audio_only.get():
        print_status('Downloading audio track...')
        audio_track.download()
        print_good('Audio track successfully downloaded.')
    else:
        video_track = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution')[-1]
        # remove all forbidden characters from the title so the script doesn't crash
        title = sanitize_string(video_track.title)

        print_status('Downloading video.mp4...')
        video_track.download(filename='video')
        print_good('video.mp4 successfully downloaded.')

        print_status('Downloading audio.mp4...')
        audio_track.download(filename='audio')
        print_good('audio.mp4 successfully downloaded.')

        print_status('Merging tracks...')
        try:
            output = subprocess.check_output(f'{merge_command} \"{title}.mp4\"', shell=True)
            print_good(f'Tracks successfully merged into \"{title}.mp4\".')
        except subprocess.CalledProcessError:
            print_error(f'Couldn\'t merge tracks. Error code: {subprocess.CalledProcessError.returncode}.')

        # delete redundant video and audio tracks
        print_status('Deleting redundant audio and video tracks...')
        result = remove_files(['video.mp4', 'audio.mp4'])
        if result == 0:
            print_good('Tracks successfully deleted.')
        else:
            print_error(f'Couldn\'t delete one or more tracks.')


if __name__ == '__main__':
    # create window and widgets

    root = tk.Tk()

    root.title('YouTube downloader by sgrontflix')
    root.option_add('*Font', '26')
    root.geometry('600x450')
    root.resizable(0, 0)

    window_title = tk.Label(root, text='YouTube downloader')

    yt_url = DTEntry(root, default_text='YouTube link here')
    ffmpeg_path = DTEntry(root, default_text='FFmpeg path here')

    gpu = tk.BooleanVar()
    audio_only = tk.BooleanVar()
    gpu_checkbox = tk.Checkbutton(root, text='Use GPU (NVIDIA only)', variable=gpu, onvalue=True, offvalue=False)
    audio_only_checkbox = tk.Checkbutton(root, text='Audio only', variable=audio_only, onvalue=True, offvalue=False)

    console_output = tk.Text(root, state='disabled', wrap='word')

    download_button = tk.Button(root, text='Download', command=handle_download)

    # place widgets on window (generated by PAGE - http://page.sourceforge.net)

    window_title.place(relx=0.233, rely=0.044, height=21, width=324)
    yt_url.place(relx=0.067, rely=0.178, height=30, relwidth=0.873)
    ffmpeg_path.place(relx=0.067, rely=0.311, height=30, relwidth=0.873)
    gpu_checkbox.place(relx=0.067, rely=0.444, relheight=0.056, relwidth=0.402)
    audio_only_checkbox.place(relx=0.717, rely=0.444, relheight=0.056, relwidth=0.218)
    console_output.place(relx=0.067, rely=0.556, relheight=0.276, relwidth=0.873)
    download_button.place(relx=0.367, rely=0.889, height=34, width=157)

    # redirect stdout and stderr to textbox
    sr = StdoutRedirector(console_output)
    sys.stdout = sr
    sys.stderr = sr

    root.mainloop()