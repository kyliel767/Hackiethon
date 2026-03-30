import pygame

def load_spritesheet(path, num_frames, row=0, scale=None):
    
    sheet = pygame.image.load(path)

    frame_width = sheet.get_width() // num_frames
    frame_height = sheet.get_height()

    frames = []
    for i in range(num_frames):
        frame = sheet.subsurface((
            i * frame_width,
            row * frame_height,
            frame_width,
            frame_height
        ))

        if scale:
            frame = pygame.transform.scale(frame, scale)
            
        frames.append(frame)

    

    return frames