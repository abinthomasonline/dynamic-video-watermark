from abc import ABC, abstractmethod
import cv2


class Animation(ABC):
    @abstractmethod
    def prepare(self, **kwargs):
        pass

    @abstractmethod
    def stamp(self, frame, **kwargs):
        pass


class HorizontalSlide(Animation):
    def __init__(self, watermark_path, fps, video_width, video_height):
        self.watermark_path = watermark_path
        self.fps = fps
        self.video_width = video_width
        self.video_height = video_height

    def prepare(self, image_width, image_height, overlay_y, slide_speed, direction="left"):
        """Prepare the watermark image for the animation. The watermark image will be resized and converted to BGRA"""
        self.watermark_img = cv2.imread(self.watermark_path, cv2.IMREAD_UNCHANGED)
        # add alpha channel to the watermark image if it does not exist
        if self.watermark_img.shape[2] == 3:
            self.watermark_img = cv2.cvtColor(self.watermark_img, cv2.COLOR_BGR2BGRA)
        
        # percentage to pixels
        if image_width == -1 and image_height == -1:
            raise ValueError("Either image_width or image_height must be specified")
        elif image_width == -1:
            self.image_height = int(self.video_height * image_height)
            self.image_width = int(self.watermark_img.shape[1] * self.image_height / self.watermark_img.shape[0])
        elif image_height == -1:
            self.image_width = int(self.video_width * image_width)
            self.image_height = int(self.watermark_img.shape[0] * self.image_width / self.watermark_img.shape[1])
        else:
            self.image_width = int(self.video_width * image_width)
            self.image_height = int(self.video_height * image_height)
        self.overlay_y = int(self.video_height * overlay_y)
        self.slide_speed = self.video_width * slide_speed
        self.direction = direction

        self.watermark_img = cv2.resize(self.watermark_img, (self.image_width, self.image_height))

    def stamp(self, frame, frame_count):
        """Stamp the watermark image on the frame"""
        # add alpha channel to the frame if it does not exist
        if frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

        seconds = frame_count / self.fps
        if self.direction == "right":
            x = int(self.slide_speed * seconds) % (self.video_width + self.image_width) - self.image_width
        elif self.direction == "left":
            x = self.video_width - int(self.slide_speed * seconds) % (self.video_width + self.image_width) - self.image_width
        else:
            raise ValueError("Invalid direction")
        y = self.overlay_y % (self.video_height + self.image_height) - self.image_height
        image = self.watermark_img[max(-y, 0): min(self.image_height, self.video_height - y), 
                                   max(-x, 0): min(self.image_width, self.video_width - x)]

        h, w = image.shape[:2]
        x, y = max(x, 0), max(y, 0)

        alpha = image[:, :, 3] / 255.0
        for c in range(0, 3):
            frame[y:y+h, x:x+w, c] = (alpha * image[:, :, c] + (1 - alpha) * frame[y:y+h, x:x+w, c])

        # remove alpha channel from the frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame
