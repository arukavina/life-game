import imageio
import os


def make_gif(frames_directory):
    # Create a list to hold the frames
    frames = []

    # Get the list of frame files
    frame_files = sorted([f for f in os.listdir(frames_directory) if f.endswith('.png')])

    # Loop through each frame file and append it to the frames list
    for file in frame_files:
        frame_path = os.path.join(frames_directory, file)
        frames.append(imageio.imread(frame_path))

    # Save the frames as a GIF
    imageio.mimsave("game_animation.gif", frames, duration=0.1)
