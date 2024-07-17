import tkinter as tk
import os
import random

# Constants and Variables
x = 1400
cycle = 0
check = 0
impath = r'C:\Users\Deepika Putta\Desktop\desktop pet\pet gif'

# Load the gifs
def load_gif(filename, frames, root):
    try:
        return [tk.PhotoImage(master=root, file=os.path.join(impath, filename), format=f'gif -index {i}') for i in range(frames)]
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

# Initialize Tkinter root window
window = tk.Tk()

# Load frames
idle = load_gif('idle.gif', 5, window)
walk = load_gif('walk.gif', 8, window)
alien = load_gif('alien.gif', 8, window)
car = load_gif('car.gif', 8, window)
boxing = load_gif('boxing.gif', 8, window)
dino = load_gif('dino.gif', 8, window)
exercise = load_gif('exercise.gif', 8, window)
fly = load_gif('fly.gif', 8, window)

# Check if frames are loaded
print(f"Idle frames loaded: {len(idle)}")
print(f"Walk frames loaded: {len(walk)}")
print(f"Alien frames loaded: {len(alien)}")
print(f"Car frames loaded: {len(car)}")
print(f"Boxing frames loaded: {len(boxing)}")
print(f"Dino frames loaded: {len(dino)}")
print(f"Exercise frames loaded: {len(exercise)}")
print(f"Fly frames loaded: {len(fly)}")

# Function to update the image based on events
def update(cycle, check, x):
    global idle, walk, alien, car, boxing, dino, exercise, fly
    print(f"Update: Cycle: {cycle}, Check: {check}, X: {x}")
    
    if check == 0:  # idle
        frames = idle
    elif check == 2:  # walk
        frames = walk
        x += 3
    elif check == 3:  # alien
        frames = alien
    elif check == 4:  # car
        frames = car
    elif check == 5:  # boxing
        frames = boxing
    elif check == 6:  # dino
        frames = dino
    elif check == 7:  # exercise
        frames = exercise
    elif check == 8:  # fly
        frames = fly
    else:
        frames = idle

    frame = frames[cycle % len(frames)]
    cycle = (cycle + 1) % len(frames)

    window.geometry(f'100x100+{x}+1050')
    label.configure(image=frame)
    label.image = frame  # Keep a reference to avoid garbage collection
    window.after(300, update, cycle, check, x)  # Increased delay to 300 milliseconds

# Function to handle event changes
def change_event():
    global check
    event_number = random.randint(1, 12)
    if event_number in idle_num:
        check = 0
    elif event_number in walk_num:
        check = 2
    elif event_number in alien_num:
        check = 3
    elif event_number in car_num:
        check = 4
    elif event_number in boxing_num:
        check = 5
    elif event_number in dino_num:
        check = 6
    elif event_number in exercise_num:
        check = 7
    elif event_number in fly_num:
        check = 8
    window.after(5000, change_event)  # Change event every 5 seconds

# Define event categories
idle_num = [1, 2, 3, 4]
walk_num = [5, 6]
alien_num = [7]
car_num = [8]
boxing_num = [9]
dino_num = [10]
exercise_num = [11]
fly_num = [12]

# Window configuration
label = tk.Label(window, bd=0, bg='white')
label.pack()

# Start the animation and event change loop
window.after(100, update, cycle, check, x)
window.after(5000, change_event)  # Start event changes
window.geometry('400x200+300+300')  # Adjust the size and position as needed
window.overrideredirect(True)
window.wm_attributes('-transparentcolor', 'white')

window.mainloop()

