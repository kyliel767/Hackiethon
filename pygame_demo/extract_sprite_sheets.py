import pygame

def load_spritesheet(path, frame_width, frame_height, num_frames, row=0):
    sheet = pygame.image.load(path)
    frames = []
    for i in range(num_frames):
        frame = sheet.subsurface((
            i * frame_width,
            row * frame_height,
            frame_width,
            frame_height
        ))
        frames.append(frame)
    return frames