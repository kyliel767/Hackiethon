import pygame

def load_spritesheet(path, num_frames, row=0):
    
    sheet = pygame.image.load(path)

    frame_width = sheet.get_width() // num_frames
    frame_height = sheet.get_height() // num_rows
    
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