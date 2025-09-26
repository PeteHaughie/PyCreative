from pycreative import Sketch
from pycreative.media import MediaPlayer

class VideoSketch(Sketch):
    def setup(self):
        self.size(640, 480)
        self.set_title("Video Playback Example")
        self.playing = False

        video_path = self.assets.load_media("ballet.mp4")
        if not video_path:
            print("Failed to load video. Make sure 'data/ballet.mp4' is in the same directory.")
            self.player = None
        else:
            self.player = MediaPlayer(video_path)
            self.player.loop = True
            self.player.video_fps = 20.0
            self.playing = True
            self.player.play()

    def draw(self):
        self.clear(0)

        if hasattr(self, "player") and self.player:
            frame_surface = self.player.resize(self.width, self.height)
            if frame_surface is not None and self._screen:
                self._screen.blit(frame_surface, (0, 0))

            if self.mouse.left_down:
                if self.playing:
                    self.player.pause()
                else:
                    self.player.resume()
                self.playing = not self.playing

    def teardown(self):
        if hasattr(self, "player") and self.player:
            self.player.stop()

if __name__ == "__main__":
    VideoSketch().run()
