import cv2
import tkinter as tk
from tkinter import filedialog, Canvas, Scrollbar, ttk


class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok-Like Video Player")

        # Scrollable Canvas
        self.canvas = Canvas(self.root)
        self.scrollbar = Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Video list and controls
        self.video_frames = []
        self.video_paths = []
        self.current_video_index = None
        self.speed_var = tk.DoubleVar(value=1.0)

        # Add Video Button
        self.add_button = tk.Button(self.root, text="Add Video", command=self.load_video)
        self.add_button.pack(pady=20)

        # Video controls
        self.playback_controls = tk.Frame(self.root)
        self.playback_controls.pack(pady=20)

        self.speed_dropdown = ttk.Combobox(self.playback_controls, textvariable=self.speed_var, values=[0.5, 1.0, 2.0],
                                           width=5)
        self.speed_dropdown.grid(row=0, column=0, padx=10)
        self.speed_dropdown.set(1.0)

        self.timeline_slider = ttk.Scale(self.playback_controls, from_=0, to=100, orient=tk.HORIZONTAL, length=300)
        self.timeline_slider.grid(row=0, column=1, padx=10)

        self.next_button = tk.Button(self.playback_controls, text="Next", command=self.next_video)
        self.next_button.grid(row=0, column=2, padx=10)

    def load_video(self):
        video_path = filedialog.askopenfilename(title="Select a Video File", filetypes=[("Video Files", "*.mp4;*.avi")])
        if not video_path:
            return

        thumbnail = self.generate_thumbnail(video_path)

        self.video_paths.append(video_path)
        video_frame = tk.Label(self.scroll_frame, image=thumbnail, bg="grey")
        video_frame.image = thumbnail  # Keep a reference to the image
        video_frame.bind("<Button-1>",
                         lambda e, path=video_path, index=len(self.video_paths) - 1: self.play_video(path, index))
        video_frame.pack(pady=10)
        self.video_frames.append(video_frame)

    def generate_thumbnail(self, video_path):
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (160, 90))
            image = cv2.imencode(".png", frame)[1].tobytes()
            thumbnail = tk.PhotoImage(data=image)
            cap.release()
            return thumbnail
        cap.release()
        return None

    def play_video(self, video_path, index):
        self.current_video_index = index

        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        paused = False

        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    break

                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                self.timeline_slider.set((current_frame / total_frames) * 100)

                cv2.imshow('Video', frame)

            key = cv2.waitKey(int(25 / self.speed_var.get()))
            if key == ord('q'):
                break
            elif key == 32:  # Space bar to pause/resume
                paused = not paused

        cap.release()
        cv2.destroyAllWindows()

    def next_video(self):
        if self.current_video_index is not None and self.current_video_index < len(self.video_paths) - 1:
            self.play_video(self.video_paths[self.current_video_index + 1], self.current_video_index + 1)


if __name__ == "__main__":
    root = tk.Tk()
    player = VideoPlayer(root)
    root.mainloop()
