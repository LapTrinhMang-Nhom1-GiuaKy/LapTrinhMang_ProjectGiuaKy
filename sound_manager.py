import os

try:
    import pygame
    _PYGAME_AVAILABLE = True
except Exception as e:
    pygame = None
    _PYGAME_AVAILABLE = False
    _PYGAME_IMPORT_ERROR = str(e)


class SoundManager:
    _initialized = False
    _sounds = {}
    _music_file = None
    _music_playing = False

    @classmethod
    def _init(cls):
        if cls._initialized:
            return
        cls._initialized = True

        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds")

        if not _PYGAME_AVAILABLE:
            print("[SoundManager] pygame not available")
            if '_PYGAME_IMPORT_ERROR' in globals():
                print("[SoundManager] import error:", _PYGAME_IMPORT_ERROR)
            return

        try:
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            print("[SoundManager] mixer init OK")
        except Exception as e:
            print("[SoundManager] mixer init failed:", e)
            return

        def load_effect(key, filename):
            path = os.path.join(SOUND_DIR, filename)
            if not os.path.isfile(path):
                print("[SoundManager] missing:", filename)
                return
            try:
                cls._sounds[key] = pygame.mixer.Sound(path)
                print("[SoundManager] loaded:", filename)
            except Exception as e:
                print("[SoundManager] load failed:", filename, e)

        # load effects
        load_effect("click", "select-button.wav")
        load_effect("win", "you-win-sound.wav")
        load_effect("lose", "you-lose-sound.wav")

        # load music
        music_path = os.path.join(SOUND_DIR, "game-music.wav")
        if os.path.isfile(music_path):
            cls._music_file = music_path
            print("[SoundManager] music ready")
        else:
            print("[SoundManager] missing: game-music.wav")

    @classmethod
    def play_click(cls):
        cls._init()
        snd = cls._sounds.get("click")
        if snd:
            snd.play()

    @classmethod
    def play_win(cls):
        cls._init()
        snd = cls._sounds.get("win")
        if snd:
            snd.play()

    @classmethod
    def play_lose(cls):
        cls._init()
        snd = cls._sounds.get("lose")
        if snd:
            snd.play()

    @classmethod
    def play_music(cls, enabled: bool):
        cls._init()
        if not cls._music_file:
            return

        try:
            if enabled and not cls._music_playing:
                pygame.mixer.music.load(cls._music_file)
                pygame.mixer.music.play(-1)
                cls._music_playing = True
            elif not enabled and cls._music_playing:
                pygame.mixer.music.stop()
                cls._music_playing = False
        except Exception as e:
            print("[SoundManager] music error:", e)
            cls._music_playing = False

    @classmethod
    def toggle_music(cls):
        cls.play_music(not cls._music_playing)
        return cls._music_playing

    @classmethod
    def is_music_playing(cls):
        return cls._music_playing

    @classmethod
    def status(cls):
        return {
            "pygame_available": _PYGAME_AVAILABLE,
            "sounds_loaded": list(cls._sounds.keys()),
            "music_file": cls._music_file,
            "music_playing": cls._music_playing,
        }
