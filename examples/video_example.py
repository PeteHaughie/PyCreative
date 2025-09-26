from pycreative import Sketch
from pycreative.media import MediaPlayer # TODO: Should this be re-exported from pycreative instead?

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
            self.player.play()
            # set initial state now that playback has started
            self.playing = True

    def draw(self):
        self.clear(0)

        self.video(self.player, 0, 0, self.width, self.height)

        if self.player is not None:
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
