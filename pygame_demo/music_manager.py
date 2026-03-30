import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
    
    def load_music(self, path, volume=0.5):
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
    
    def play_music(self, loops=-1):
        pygame.mixer.music.play(loops)
    
    def stop_music(self):
        pygame.mixer.music.stop()
    
    def load_sound(self, name, path):
        self.sounds[name] = pygame.mixer.Sound(path)
    
    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()
