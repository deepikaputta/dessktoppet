import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import os
import time
import threading
import pygame

class DesktopPet:
    def __init__(self, root, gif_paths, sound_path):
        self.root = root
        self.root.title("Desktop Pet")
        self.root.geometry("400x300")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.config(bg='grey')
        self.root.wm_attributes("-transparentcolor", "grey")

        # Load GIFs and remove background
        self.animations = {}
        self.original_animations = {}
        self.special_animations = ['med', 'eat', 'sleep', 'tab', 'note', 'win']
        for key, path in gif_paths.items():
            frames = self.load_and_remove_bg(path, (128, 128, 128))
            self.original_animations[key] = frames
            self.animations[key] = [ImageTk.PhotoImage(frame) for frame in frames]

        # Initialize Pygame for sound
        pygame.mixer.init()
        self.reminder_sound = sound_path

        # Create Canvas
        self.canvas = tk.Canvas(self.root, width=400, height=300, highlightthickness=0, bg="grey")
        self.canvas.pack()
        self.pet_image = self.canvas.create_image(200, 150, image=self.animations['walk'][0])

        # Animation Attributes
        self.current_animation = self.animations['walk']
        self.current_animation_key = 'walk'
        self.current_frame = 0

        # Position Attributes
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.x, self.y = self.screen_width // 2, self.screen_height // 2
        self.dx = 5  # Horizontal movement delta

        # Dragging Attributes
        self.dragging = False

        # Tasks Attributes
        self.tasks = {}

        # Start Animation
        self.animate()

        # Bind Mouse Events
        self.canvas.bind("<Button-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)
        self.canvas.bind("<Button-3>", self.switch_animation)

        # Automatic animation switch every 1 minute
        self.root.after(60000, self.auto_switch_animation)
        
        # Schedule special GIFs display at specific times
        self.schedule_special_gifs()

        # Create User Interface
        self.create_task_input_ui()

    def load_and_remove_bg(self, gif_path, bg_color):
        gif = Image.open(gif_path)
        frames = []
        tolerance = 50  # Tolerance level for background color removal
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert("RGBA")
            datas = frame.getdata()
            new_data = []
            for item in datas:
                # Remove background color within the tolerance level
                if all(abs(item[i] - bg_color[i]) < tolerance for i in range(3)):
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            frame.putdata(new_data)
            frames.append(frame)
        return frames

    def animate(self):
        self.current_frame = (self.current_frame + 1) % len(self.current_animation)
        self.canvas.itemconfig(self.pet_image, image=self.current_animation[self.current_frame])
        self.move_pet()
        self.root.after(100, self.animate)  # Adjust this to 200 or 300 if the animations are too fast

    def move_pet(self):
        # Update position horizontally only if the current animation is 'walk' and not dragging
        if self.current_animation_key == 'walk' and not self.dragging:
            self.x += self.dx

            # Boundary conditions to reverse direction
            if self.x <= 0 or self.x >= self.screen_width:
                self.dx = -self.dx
                self.flip_pet_image()

            # Move the pet image
            self.root.geometry(f'+{self.x}+{self.y}')

    def flip_pet_image(self):
        # Flip the original PIL image frames horizontally
        for key in self.animations:
            flipped_frames = [frame.transpose(Image.FLIP_LEFT_RIGHT) for frame in self.original_animations[key]]
            self.animations[key] = [ImageTk.PhotoImage(frame) for frame in flipped_frames]

    def switch_animation(self, event=None):
        # Switch to the next animation in the list, excluding special animations
        animation_keys = [key for key in self.animations.keys() if key not in self.special_animations]
        current_index = animation_keys.index(self.current_animation_key)
        next_index = (current_index + 1) % len(animation_keys)
        next_animation_key = animation_keys[next_index]
        self.current_animation = self.animations[next_animation_key]
        self.current_animation_key = next_animation_key
        self.current_frame = 0

    def auto_switch_animation(self):
        self.switch_animation()
        self.root.after(60000, self.auto_switch_animation)

    def on_drag_start(self, event):
        self.dragging = True
        self.start_x = event.x
        self.start_y = event.y

    def on_drag_motion(self, event):
        deltax = event.x - self.start_x
        deltay = event.y - self.start_y
        self.x += deltax
        self.y += deltay
        self.root.geometry(f'+{self.x}+{self.y}')

    def on_drag_end(self, event):
        self.dragging = False

    def schedule_special_gifs(self):
        med_times = ["05:00", "08:00", "14:00", "17:00", "21:00"]
        eat_times = ["07:30", "12:30", "19:30"]
        sleep_times = ["23:00"]
        current_time = time.strftime("%H:%M")
        
        for med_time in med_times:
            self.schedule_gif(med_time, 'med')

        for eat_time in eat_times:
            self.schedule_gif(eat_time, 'eat')

        for sleep_time in sleep_times:
            self.schedule_gif(sleep_time, 'sleep')

    def schedule_gif(self, special_time, gif_key):
        hour, minute = map(int, special_time.split(":"))
        special_time_sec = hour * 3600 + minute * 60
        current_time_sec = int(time.strftime("%H")) * 3600 + int(time.strftime("%M")) * 60
        delay = special_time_sec - current_time_sec
        if delay < 0:
            delay += 86400  # Add 24 hours in seconds if the time has already passed
        self.root.after(delay * 1000, lambda: self.show_special_gif(gif_key))

    def show_special_gif(self, gif_key):
        self.previous_animation = self.current_animation
        self.current_animation = self.animations[gif_key]
        self.current_animation_key = gif_key
        self.current_frame = 0
        self.root.after(600000, self.restore_previous_animation)  # 10 minutes

    def restore_previous_animation(self, event=None):
        if self.previous_animation in self.animations.values():
            self.current_animation = self.previous_animation
            self.current_animation_key = [key for key, anim in self.animations.items() if anim == self.previous_animation][0]
            self.current_frame = 0
            self.schedule_special_gifs()  # Reschedule for the next occurrence

    def create_task_input_ui(self):
        self.task_window = tk.Toplevel(self.root)
        self.task_window.geometry("500x400")
        self.task_window.title("Task Input")
        self.task_window.config(bg='#6a0dad')

        self.task_frame = ttk.Frame(self.task_window, padding="10 10 10 10")
        self.task_frame.pack(fill=tk.BOTH, expand=True)

        self.add_task_ui()

        self.task_list_frame = ttk.Frame(self.task_window, padding="10 10 10 10")
        self.task_list_frame.pack(fill=tk.BOTH, expand=True)

        self.update_task_list()

    def add_task_ui(self):
        self.add_task_frame = ttk.Frame(self.task_frame)
        self.add_task_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.add_task_frame, text="Task:", font=('Helvetica', 12)).grid(row=0, column=0, padx=5, pady=5)
        self.task_entry = ttk.Entry(self.add_task_frame, font=('Helvetica', 12))
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)
        self.task_entry.bind("<FocusIn>", self.show_note_gif)
        self.task_entry.bind("<FocusOut>", self.restore_previous_animation)

        ttk.Label(self.add_task_frame, text="Complete by (HH:MM):", font=('Helvetica', 12)).grid(row=1, column=0, padx=5, pady=5)
        self.deadline_entry = ttk.Entry(self.add_task_frame, font=('Helvetica', 12))
        self.deadline_entry.grid(row=1, column=1, padx=5, pady=5)
        self.deadline_entry.bind("<FocusIn>", self.show_note_gif)
        self.deadline_entry.bind("<FocusOut>", self.restore_previous_animation)

        ttk.Button(self.add_task_frame, text="Add Task", command=self.submit_task).grid(row=2, columnspan=2, pady=10)

    def show_note_gif(self, event=None):
        self.previous_animation = self.current_animation
        self.current_animation = self.animations['note']
        self.current_animation_key = 'note'
        self.current_frame = 0

    def submit_task(self):
        task = self.task_entry.get()
        deadline = self.deadline_entry.get()
        if task and deadline:
            self.tasks[task] = {'deadline': deadline, 'done': False}
            self.update_task_list()
            self.check_task_completion(task, deadline)
            self.schedule_reminder(task, deadline)

    def update_task_list(self):
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        for task, details in self.tasks.items():
            task_frame = ttk.Frame(self.task_list_frame)
            task_frame.pack(fill=tk.X, pady=2)

            task_label = ttk.Label(task_frame, text=f"{task} - Due by {details['deadline']}" if not details['done'] else f"{task} - Done", font=('Helvetica', 12))
            task_label.pack(side=tk.LEFT, padx=10)

            if not details['done']:
                done_button = ttk.Button(task_frame, text="Done", command=lambda t=task: self.mark_task_done(t))
                done_button.pack(side=tk.RIGHT, padx=10)

    def mark_task_done(self, task):
        self.tasks[task]['done'] = True
        self.update_task_list()
        self.show_special_gif('win')

    def check_task_completion(self, task, deadline):
        deadline_hour, deadline_minute = map(int, deadline.split(":"))
        deadline_sec = deadline_hour * 3600 + deadline_minute * 60
        current_time_sec = int(time.strftime("%H")) * 3600 + int(time.strftime("%M")) * 60
        delay = deadline_sec - current_time_sec
        if delay < 0:
            delay += 86400  # Add 24 hours in seconds if the deadline has already passed for the day
        self.root.after(delay * 1000, lambda t=task: self.show_angry_if_task_not_completed(t))

    def schedule_reminder(self, task, deadline):
        deadline_hour, deadline_minute = map(int, deadline.split(":"))
        deadline_sec = deadline_hour * 3600 + deadline_minute * 60
        current_time_sec = int(time.strftime("%H")) * 3600 + int(time.strftime("%M")) * 60
        delay = deadline_sec - current_time_sec - 3600  # 1 hour before the deadline
        if delay < 0:
            delay += 86400  # Add 24 hours in seconds if the reminder time has already passed for the day
        self.root.after(delay * 1000, lambda t=task: self.show_reminder_gif_and_sound(t))

    def show_reminder_gif_and_sound(self, task):
        if not self.tasks[task]['done']:  # If task is still not completed
            self.show_special_gif('tab')
            pygame.mixer.music.load(self.reminder_sound)
            pygame.mixer.music.play()

    def show_angry_if_task_not_completed(self, task):
        if not self.tasks[task]['done']:  # If task is still not completed
            self.show_special_gif('angry')

# Main Execution
if __name__ == "__main__":
    root = tk.Tk()
    gif_paths = {
        'walk': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\walk.gif",
        'time': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\time.gif",
        'alien': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\alien.gif",
        'idle': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\idle.gif",
        'dab': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\dab.gif",
        'med': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\med.gif",
        'eat': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\eat.gif",
        'sleep': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\sleep.gif",
        'angry': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\angry.gif",
        'note': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\note.gif",
        'win': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\win.gif",
        'tab': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\tab.gif",
        'books': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\books.gif",
        'drum': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\drum.gif",
        'fly': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\fly.gif",
        'box': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\box.gif",
        'work': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\work.gif",
        'sing': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\sing.gif",
        'plant': r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\plant.gif"
    }  # Replace with your actual paths to the GIFs
    sound_path = r"C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2\Reminder.mp3"  # Replace with your actual path to the reminder sound
    pet = DesktopPet(root, gif_paths, sound_path)
    root.mainloop()




