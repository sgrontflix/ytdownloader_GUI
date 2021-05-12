from utilities import *
from gui_classes import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from threading import Thread
from pathlib import Path
from pytube import YouTube
import sys


def browse():
    """
    Lets the user select the FFmpeg executable by opening a file browser window

    :return: None
    """

    # open file explorer inside the ytdownloader_GUI directory
    # you can select .exe files (windows only) or all files (linux)
    filename = filedialog.askopenfilename(initialdir='.', title='Select FFmpeg executable',
                                          filetypes=(('Executable files', '*.exe'), ('All files', '*.*')))

    # clear input field before inserting new path
    ffmpeg_path.delete(0, tk.END)
    ffmpeg_path.config(fg='black')
    ffmpeg_path.insert(0, filename)


def handle_download():
    """
    Handles the audio/video download by disabling all the input fields,
    starting the actual download thread and calling the thread monitoring function

    :return: None
    """
    for widget in root.winfo_children():
        if widget is gpu_checkbox:
            if gpu_exists:
                widget.config(state='disabled')
        elif not isinstance(widget, tk.Label) and not isinstance(widget, tk.Text) and not isinstance(widget, tk.Menu):
            widget.config(state='disabled')

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
        for widget in root.winfo_children():
            if isinstance(widget, ttk.Combobox):
                widget.config(state='readonly')
            elif widget is gpu_checkbox:
                if gpu_exists:
                    widget.config(state='normal')
            elif not isinstance(widget, tk.Label) and not isinstance(widget, tk.Text) \
                    and not isinstance(widget, tk.Menu):
                widget.config(state='normal')


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

    if not youtube_url_validation(yt_url.get()):
        messagebox.showerror('ERROR', 'Invalid URL detected')
        return

    if not Path(ffmpeg_path.get()).is_file():
        messagebox.showerror('ERROR', 'Invalid path detected')
        return

    # get yt link info
    yt = YouTube(yt_url.get())

    audio_track = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('bitrate')[-1]

    # remove all forbidden characters from the title so the script doesn't crash
    title = sanitize_string(audio_track.title)

    if audio_only.get():
        print_status('Downloading audio track...')
        audio_path = audio_track.download(filename=title)
        if audio_track.exists_at_path(audio_path):
            print_good(f'{title}.mp4 successfully downloaded.')
        else:
            print_error('Couldn\'t download audio track.')
            
            if Path(audio_path).is_file():
                print_status('Cleaning up...')
                result = remove_files([f'{title}.mp4'])
                # a list is False if empty, True if not
                if not result:
                    print_good(f'{title}.mp4 deleted.')
                else:
                    print_error(f'Couldn\'t delete {title}.mp4.')
    else:
        enable_gpu = ' -hwaccel cuda -hwaccel_output_format cuda'
        merge_command = '\"' + ffmpeg_path.get() + '\" -y' + (enable_gpu if gpu.get() else '') + \
                        ' -hide_banner -loglevel panic -i video.mp4 -i audio.mp4 -c:v copy -c:a copy'

        video_track = \
            yt.streams.filter(progressive=False, file_extension='mp4', resolution=resolution.get()).order_by('fps')

        # if at least a video track with the given resolution was found, select the best one (highest fps)
        if video_track:
            video_track = video_track[-1]
        # otherwise select the video track with the highest possible resolution and fps
        else:
            print_error('Missing video track for the given resolution.')
            print_status('Selecting the highest possible resolution video track.')
            video_track = \
                yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').order_by('fps')[-1]

        print_status('Downloading video.mp4...')
        video_path = video_track.download(filename='video')
        if video_track.exists_at_path(video_path):
            print_good('video.mp4 successfully downloaded.')
        else:
            print_error('Couldn\'t download video.mp4.')

            if Path(video_path).is_file():
                print_status('Cleaning up...')
                result = remove_files(['video.mp4'])
                if not result:
                    print_good('video.mp4 deleted.')
                else:
                    print_error('Couldn\'t delete video.mp4.')

            return

        print_status('Downloading audio.mp4...')
        audio_path = audio_track.download(filename='audio')
        if audio_track.exists_at_path(audio_path):
            print_good('audio.mp4 successfully downloaded.')
        else:
            print_error('Couldn\'t download audio.mp4.')

            print_status('Cleaning up...')
            result = remove_files(['video.mp4'])
            if not result:
                print_good('video.mp4 deleted.')
            else:
                print_error('Couldn\'t delete video.mp4.')

            if Path(audio_path).is_file():
                result = remove_files(['audio.mp4'])
                if not result:
                    print_good('audio.mp4 deleted.')
                else:
                    print_error('Couldn\'t delete audio.mp4.')

            return

        print_status('Merging tracks...')
        try:
            output = subprocess.check_output(f'{merge_command} \"{title}.mp4\"', shell=True)
            print_good(f'Tracks successfully merged into \"{title}.mp4\".')
        except subprocess.CalledProcessError:
            print_error(f'Couldn\'t merge tracks. Error code: {subprocess.CalledProcessError.returncode}.')

        # delete redundant video and audio tracks
        print_status('Deleting redundant audio and video tracks...')
        result = remove_files(['video.mp4', 'audio.mp4'])
        if not result:
            print_good('Tracks successfully deleted.')
        else:
            print_error('Couldn\'t delete the following track(s): ' + ', '.join([str(track) for track in result]) + '.')


if __name__ == '__main__':
    # create window and widgets

    root = tk.Tk()

    root.title('YouTube downloader by sgrontflix')
    root.option_add('*Font', 'Arial 16')
    root.geometry('813x450')
    root.resizable(0, 0)

    resolution_list = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
    resolution = tk.StringVar()
    gpu = tk.BooleanVar()
    audio_only = tk.BooleanVar()

    # check if NVIDIA GPU exists
    gpu_exists = is_gpu_available()

    window_title = tk.Label(root, text='YouTube downloader')
    yt_url = DTEntry(root, default_text='YouTube link here')
    resolution_menu = ttk.Combobox(root, textvariable=resolution, values=resolution_list, state='readonly')
    # set default value (index 0, first element)
    resolution_menu.current(0)
    ffmpeg_path = DTEntry(root, default_text='FFmpeg path here')
    browse_button = tk.Button(root, text='Browse', command=browse)
    gpu_checkbox = tk.Checkbutton(root, text='Use GPU (NVIDIA only)', variable=gpu,
                                  command=lambda: audio_only.set(False))
    # disable checkbox if NVIDIA GPU does not exist
    if not gpu_exists:
        gpu_checkbox.config(state='disabled')
    audio_only_checkbox = tk.Checkbutton(root, text='Audio only', variable=audio_only, command=lambda: gpu.set(False))
    console_output = tk.Text(root, state='disabled', wrap='word')
    download_button = tk.Button(root, text='Download', command=handle_download)

    # place widgets on window (generated by PAGE - http://page.sourceforge.net)

    window_title.place(relx=0.232, rely=0.044, height=21, width=435)
    yt_url.place(relx=0.068, rely=0.178, height=30, relwidth=0.695)
    resolution_menu.place(relx=0.8, rely=0.178, height=34, width=117)
    ffmpeg_path.place(relx=0.068, rely=0.311, height=30, relwidth=0.695)
    browse_button.place(relx=0.812, rely=0.311, height=34, width=97)
    gpu_checkbox.place(relx=0.062, rely=0.444, relheight=0.056, relwidth=0.316)
    audio_only_checkbox.place(relx=0.776, rely=0.444, relheight=0.056, relwidth=0.166)
    console_output.place(relx=0.068, rely=0.556, relheight=0.276, relwidth=0.866)
    download_button.place(relx=0.401, rely=0.889, height=34, width=159)

    # redirect stdout and stderr to textbox
    sr = StdoutRedirector(console_output)
    sys.stdout = sr
    sys.stderr = sr

    # add context menu to yt_url and ffmpeg_path
    menu = ContextMenu([yt_url, ffmpeg_path], root)

    root.mainloop()
