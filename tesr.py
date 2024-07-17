import tkinter as tk
import os

impath = r'C:\Users\Deepika Putta\Desktop\desktop pet\pet gif2'

# Load the alien.gif
def load_gif(filename, frames, root):
    try:
        return [tk.PhotoImage(master=root, file=os.path.join(impath, filename), format=f'gif -index {i}') for i in range(frames)]
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

# Function to update the image
def update(cycle):
    global alien
    frame = alien[cycle]
    cycle = (cycle + 1) % len(alien)
    label.configure(image=frame)
    label.image = frame  # Keep a reference to avoid garbage collection
    window.after(100, update, cycle)  # Adjust the delay as needed

# Initialize Tkinter root window
window = tk.Tk()

# Load frames
alien = load_gif('idle.gif', 8, window)

# Check if frames are loaded
print(f"Alien frames loaded: {len(alien)}")
for i, frame in enumerate(alien):
    if frame:
        print(f"Frame {i} loaded successfully.")
    else:
        print(f"Frame {i} failed to load.")

# Window configuration
label = tk.Label(window, bd=0, bg='white')
label.pack()

# Start the animation loop
window.after(100, update, 0)
window.geometry('400x200+300+300')  # Adjust the size and position as needed
window.overrideredirect(True)
window.wm_attributes('-transparentcolor', 'white')

window.mainloop()

