from pycreative import Sketch
from pycreative.audio import AudioPlayer

class AudioSketch(Sketch):
    def setup(self):
        self.size(400, 200)
        self.set_title("Audio Playback Example")
        self.bg = (0, 0, 0)
        audio_path = self.assets.load_media("groove.mp3")
        self.playing = False
        if not audio_path:
            print("Failed to load audio. Make sure 'examples/data/groove.mp3' exists.")
            self.player = None
        else:
            self.player = AudioPlayer(audio_path)
            self.player.loop = True
            self.player.set_volume(0.7)
            self.playing = True
            self.player.play()
            self.bg = (0, 255, 0)

    def draw(self):
        self.clear(self.bg)
        # Draw simple UI
        self.text(
            "Click to Play/Pause", 200, 100, center=True, color=(40, 40, 80), size=24
        )
        # Handle play/pause toggle
        if self.mouse.left_down and self.player:
            if self.playing:
                self.player.pause()
                self.bg = (255, 0, 0)
            else:
                self.player.resume()
                self.bg = (0, 255, 0)
            self.playing = not self.playing

    def teardown(self):
        if hasattr(self, "player") and self.player:
            self.player.stop()

if __name__ == "__main__":
    AudioSketch().run()
