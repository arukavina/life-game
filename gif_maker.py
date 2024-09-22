import imageio.v2 as imageio
import os
import re


def sort_filenames(files):
    # Extract the numeric part from each file and use it for sorting
    sorted_files = sorted(files, key=lambda x: int(re.findall(r'\d+', x)[0]))
    return sorted_files


def make_gif(frames_directory, _dir):
    # Create a list to hold the frames
    frames = []

    # Get the list of frame files
    frame_files = sort_filenames([f for f in os.listdir(frames_directory) if f.endswith('.png')])

    # Loop through each frame file and append it to the frames list
    for file in frame_files:
        frame_path = os.path.join(frames_directory, file)
        frames.append(imageio.imread(frame_path))

    # Save the frames as a GIF
    imageio.mimsave(f'{_dir}/gol.gif', frames, duration=0.1)
