#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python-based implementation of Conway's Game of Life, built using **Pygame**. The simulation runs an interactive version
of the Life-Game, complete with a generation counter, time elapsed, and logic to detect when the generations stabilize
or repeat.

GNU General Public License v3.0
"""

# Built-in/Generic Imports
import os
import shutil
import sys
import time

# Libs
import numpy as np
import pygame

# Own modules
import gif_maker as gm

np.set_printoptions(threshold=70)

# Constants
GRID_SIZE = 16  # Size of grid
CELL_SIZE = 30  # Each cell's pixel size
WINDOW_SIZE = GRID_SIZE * CELL_SIZE  # 640x640 window
TOP_SECTION_HEIGHT = 60  # Extra space for the top section (title bar)
SCREEN_HEIGHT = WINDOW_SIZE + TOP_SECTION_HEIGHT
BG_IMAGE = 'static/media/bg.jpg'

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

NUMBER_OF_INITIAL_CELLS = 12

# Initialize PyGame
pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, SCREEN_HEIGHT))
pygame.display.set_caption('Life-Game')
clock = pygame.time.Clock()

font_large = pygame.font.SysFont('Arial', 24)
font_small = pygame.font.SysFont('Arial', 18)

# Load background image
background = pygame.image.load(BG_IMAGE)
background = pygame.transform.scale(background, (WINDOW_SIZE, WINDOW_SIZE))

frames_directory = "static/media/frames"

# Re-Create a directory to store frames
shutil.rmtree(frames_directory, ignore_errors=True)
os.makedirs(frames_directory)


# Function to draw grid
def draw_grid():
    for x in range(0, WINDOW_SIZE, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, TOP_SECTION_HEIGHT), (x, SCREEN_HEIGHT))
    for y in range(TOP_SECTION_HEIGHT, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WINDOW_SIZE, y))


# Function to draw the top section (generation counter, time, message)
def draw_top_section(generation, elapsed_time, cell_count, blinking, frozen, empty):
    screen.fill(BLACK, (0, 0, WINDOW_SIZE, TOP_SECTION_HEIGHT))

    # Create the generation and time text
    text_gen = font_large.render(f'Generation: {generation}', True, WHITE)
    text_time = font_large.render(f'Time: {elapsed_time:.2f} s', True, WHITE)
    text_cells = font_small.render(f'Active Cells: {cell_count}', True, WHITE)

    # Calculate positions to justify them horizontally
    total_width = text_gen.get_width() + text_time.get_width()

    # Render the texts in the top section
    screen.blit(text_gen, (10, 10))
    screen.blit(text_time, (WINDOW_SIZE // 2 - text_time.get_width() // 2, 10))
    screen.blit(text_cells, (WINDOW_SIZE // 2 - text_cells.get_width() // 2, 35))

    pygame.display.update()


def draw_top_end_state(msg):
    message_text = font_large.render(msg, True, RED)
    screen.blit(message_text, (WINDOW_SIZE - message_text.get_width() - 10, 10))
    pygame.display.update()


# Function to get cell coordinates from mouse position
def get_cell_from_mouse(pos):
    x, y = pos
    if y <= TOP_SECTION_HEIGHT:
        return None
    return x // CELL_SIZE, (y - TOP_SECTION_HEIGHT) // CELL_SIZE


# Function to draw a cell
def draw_cell(cell, color):
    rect = pygame.Rect(cell[0] * CELL_SIZE, (cell[1] * CELL_SIZE) + TOP_SECTION_HEIGHT, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, color, rect)


# Main Game Loop
def main():
    current_generation = set()
    previous_generation = set()
    running = True
    game_started = False
    generation = 0
    elapsed_time = 0
    cell_count = 0

    screen.blit(background, (0, TOP_SECTION_HEIGHT))
    draw_grid()
    pygame.display.flip()

    paused = False
    blinking = False
    frozen = False
    empty = False

    draw_top_section(generation, elapsed_time, cell_count, blinking, frozen, empty)

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle mouse click
            if event.type == pygame.MOUSEBUTTONDOWN and not game_started:
                if len(current_generation) < NUMBER_OF_INITIAL_CELLS:
                    cell = get_cell_from_mouse(pygame.mouse.get_pos())
                    if not cell:
                        break
                    if cell not in current_generation:
                        current_generation.add(cell)
                        draw_top_section(generation, elapsed_time, len(current_generation), blinking, frozen, empty)
                        draw_cell(cell, RED)
                        pygame.display.update()
                if len(current_generation) == NUMBER_OF_INITIAL_CELLS:
                    start_time = time.time()
                    game_started = True
                    print("Game started with cells:", current_generation)

        if game_started and not paused and not frozen and not empty:

            elapsed_time = time.time() - start_time
            cell_count = len(current_generation)
            draw_top_section(generation, elapsed_time, cell_count, blinking, frozen, empty)

            pygame.image.save(screen, f"{frames_directory}/frame_{generation}.png")

            screen.blit(background, (0, TOP_SECTION_HEIGHT))
            draw_grid()
            pygame.display.flip()

            next_generation = compute_next_generation(current_generation)

            # Check if the new generation is the same as the previous one
            if len(next_generation) == 0:
                draw_top_end_state("Dead Gen")
                paused = True

            # Check if the new generation is the same as the previous one
            elif next_generation == previous_generation:
                draw_top_end_state("Blinking Gen")
                paused = True

            # Check if the new generation is the same as the current one
            elif next_generation == current_generation:
                draw_top_end_state("Frozen Gen")
                paused = True

            if paused:
                # Draw current gen cells in blue
                for cell in current_generation:
                    draw_cell(cell, BLUE)

            # Draw new cells in red
            for cell in next_generation:
                draw_cell(cell, RED)

            pygame.display.update()

            # Update previous generation
            previous_generation = current_generation
            current_generation = next_generation

            generation += 1

        clock.tick(35)

    pygame.image.save(screen, f"{frames_directory}/frame_{generation}.png")
    gm.make_gif(frames_directory, 'static/media')
    pygame.quit()
    sys.exit()


# Check if two cells are neighbors (including diagonally)
def are_neighbors(cell1, cell2):
    return abs(cell1[0] - cell2[0]) <= 1 and abs(cell1[1] - cell2[1]) <= 1


# Function to create the next generation of cells on the current generation
def compute_next_generation(selected_cells):
    candidates = set()
    next_generation = set()

    for cell in selected_cells:
        for row in range(max(0, cell[0] - 1), min(GRID_SIZE, cell[0] + 2)):
            for col in range(max(0, cell[1] - 1), min(GRID_SIZE, cell[1] + 2)):
                if (row, col) != cell:
                    candidates.add((row, col))

    neighbors = candidates.union(selected_cells)
    neighbor_counts = {cell: 0 for cell in candidates.union(selected_cells)}

    for cell in neighbors:
        neighbors_count = sum(
            are_neighbors(cell, other_cell)
            for other_cell in selected_cells
            if cell != other_cell
        )

        if neighbors_count > 0:
            neighbor_counts[cell] = neighbors_count

    for cell, count in neighbor_counts.items():
        if cell in selected_cells:
            if count in (2, 3):
                # Survives
                next_generation.add(cell)
        elif count == 3:
            # Becomes Alive
            next_generation.add(cell)

    return next_generation


if __name__ == "__main__":
    main()
