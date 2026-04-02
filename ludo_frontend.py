from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import math
import random
import threading
import time
import cv2
import numpy as np
_theme_thread = None
_theme_stop_flag = None

def _center_window(win, width, height):
    try:
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")
    except Exception:
        try:
            win.geometry(f"{width}x{height}")
        except Exception:
            pass

def start_theme_music():
    global _theme_thread, _theme_stop_flag
    try:
        if _theme_thread and _theme_thread.is_alive():
            return
        _theme_stop_flag = threading.Event()
        def _loop():
            while _theme_stop_flag and not _theme_stop_flag.is_set():
                try:
                    try:
                        from playsound import playsound
                        playsound("sounds/theme.mp3", block=True)
                    except Exception:
                        # Fallback: try winsound with wav not available; skip
                        time.sleep(1.5)
                except Exception:
                    time.sleep(1.0)
        _theme_thread = threading.Thread(target=_loop, daemon=True)
        _theme_thread.start()
    except Exception:
        pass

def stop_theme_music():
    global _theme_thread, _theme_stop_flag
    try:
        if _theme_stop_flag:
            _theme_stop_flag.set()
    except Exception:
        pass

class SplashScreen:
    def __init__(self, root, on_complete_callback):
        self.window = root
        self.on_complete = on_complete_callback
        self.window.geometry("800x630")
        self.window.maxsize(800, 630)
        self.window.minsize(800, 630)
        self.window.title("AI Ludo Game")
        self.window.configure(bg="black")
        
        # Remove window decorations for splash effect
        self.window.overrideredirect(True)
        
        # Center window on screen
        self.center_window()
        
        # Create canvas
        self.canvas = Canvas(self.window, bg="black", width=800, height=630, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=1)
        
        # Animation variables
        self.alpha = 0
        self.fade_in = True
        self.text_phase = 0  # 0: fade in, 1: display, 2: fade out
        self.video_cap = None
        
        # Start the sequence
        self.show_text()
        # Start theme music on app open
        try:
            start_theme_music()
        except Exception:
            pass
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (630 // 2)
        self.window.geometry(f"800x630+{x}+{y}")
    
    def show_text(self):
        # Clear canvas
        self.canvas.delete("all")
        
        # Create text with glow effect
        self.canvas.create_text(400, 280, text="Presented by", 
                              font=("Arial", 24, "italic"), 
                              fill="#666666", tags="by_text")
        
        self.canvas.create_text(400, 320, text="Sumaiya & Maariya", 
                              font=("Arial", 36, "bold"), 
                              fill="#ffffff", tags="names")
        
        # Add glow effect
        self.canvas.create_text(402, 322, text="Sumaiya & Maariya", 
                              font=("Arial", 36, "bold"), 
                              fill="#4ecdc4", tags="names_glow")
        self.canvas.tag_lower("names_glow")
        
        # Start text animation
        self.animate_text()
    
    def animate_text(self):
        if self.text_phase == 0:  # Fade in
            self.alpha += 0.05
            if self.alpha >= 1:
                self.alpha = 1
                self.text_phase = 1
                # Schedule fade out after 3 seconds
                self.window.after(3000, lambda: setattr(self, 'text_phase', 2))
        
        elif self.text_phase == 2:  # Fade out
            self.alpha -= 0.05
            if self.alpha <= 0:
                self.alpha = 0
                # Start video playback
                self.play_video()
                return
        
        # Update text opacity (simulate with color intensity)
        intensity = int(255 * self.alpha)
        text_color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
        glow_color = f"#{int(intensity * 0.3):02x}{int(intensity * 0.8):02x}{int(intensity * 0.8):02x}"
        
        # Update colors
        items = self.canvas.find_withtag("names")
        if items:
            self.canvas.itemconfig(items[0], fill=text_color)
        
        items = self.canvas.find_withtag("names_glow")
        if items:
            self.canvas.itemconfig(items[0], fill=glow_color)
        
        items = self.canvas.find_withtag("by_text")
        if items:
            self.canvas.itemconfig(items[0], fill=f"#{int(intensity * 0.4):02x}{int(intensity * 0.4):02x}{int(intensity * 0.4):02x}")
        
        # Schedule next frame
        self.window.after(50, self.animate_text)
    
    def play_video(self):
        try:
            # Clear canvas
            self.canvas.delete("all")
            
            # Initialize video capture
            self.video_cap = cv2.VideoCapture("ludo.mp4")
            
            if not self.video_cap.isOpened():
                print("Warning: Could not open video file. Skipping video...")
                self.smooth_transition_to_menu()
                return
            
            # Get video properties
            fps = self.video_cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 5
            
            print(f"Video: {frame_count} frames, {fps} FPS, {duration:.2f} seconds")
            
            # Play video
            self.current_frame_photo = None
            self.play_video_frames()
            
        except Exception as e:
            print(f"Error playing video: {e}")
            self.smooth_transition_to_menu()
    
    def play_video_frames(self):
        if not self.video_cap:
            self.smooth_transition_to_menu()
            return
            
        ret, frame = self.video_cap.read()
        
        if ret:
            try:
                # Resize frame to fit canvas
                frame = cv2.resize(frame, (800, 630))
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                self.current_frame_photo = ImageTk.PhotoImage(pil_image)
                
                # Display frame
                self.canvas.delete("video_frame")
                self.canvas.create_image(400, 315, image=self.current_frame_photo, tags="video_frame")
                
                # Calculate delay for proper FPS
                fps = self.video_cap.get(cv2.CAP_PROP_FPS)
                delay = int(1000 / fps) if fps > 0 else 33  # Default to ~30fps
                
                # Schedule next frame
                self.window.after(delay, self.play_video_frames)
            except Exception as e:
                print(f"Error processing video frame: {e}")
                self.smooth_transition_to_menu()
        else:
            # Video ended
            if self.video_cap:
                self.video_cap.release()
                self.video_cap = None
            print("Video playback completed")
            self.smooth_transition_to_menu()
    
    def smooth_transition_to_menu(self):
        # Create a smooth black overlay that gradually covers the screen
        self.fade_alpha = 0.0
        self.fade_rectangles = []
        self.smooth_fade_out()
    
    def smooth_fade_out(self):
        self.fade_alpha += 0.03  # Slower, smoother fade
        
        if self.fade_alpha >= 1.0:
            # Fade complete, show menu
            self.window.destroy()
            self.on_complete()
            return
        
        # Clear previous fade rectangles
        for rect in self.fade_rectangles:
            self.canvas.delete(rect)
        self.fade_rectangles.clear()
        
        # Create multiple overlapping rectangles for smooth fade effect
        num_layers = int(self.fade_alpha * 10) + 1  # 1-10 layers based on fade progress
        
        for i in range(num_layers):
            # Calculate darkness for each layer
            layer_alpha = min(1.0, self.fade_alpha + (i * 0.1))
            darkness = int(50 * layer_alpha)  # Max darkness value
            
            # Create color (getting darker)
            fade_color = f"#{darkness:02x}{darkness:02x}{darkness:02x}"
            
            # Create rectangle
            rect = self.canvas.create_rectangle(
                0, 0, 800, 630, 
                fill=fade_color,
                outline="",
                tags="fade_overlay"
            )
            self.fade_rectangles.append(rect)
        
        # Create final black overlay when fade is advanced enough
        if self.fade_alpha > 0.7:
            final_darkness = int(255 * ((self.fade_alpha - 0.7) / 0.3))
            final_color = f"#{final_darkness:02x}{final_darkness:02x}{final_darkness:02x}"
            final_rect = self.canvas.create_rectangle(
                0, 0, 800, 630,
                fill=final_color,
                outline="",
                tags="fade_overlay"
            )
            self.fade_rectangles.append(final_rect)
        
        # Schedule next frame
        self.window.after(40, self.smooth_fade_out)

class GameModeSelector:
    def __init__(self, root, on_mode_selected, parent_window):
        self.window = root
        self.on_mode_selected = on_mode_selected
        self.parent_window = parent_window  # Store reference to parent
        self.window.geometry("650x500")  # Increased height for the third button
        self.window.title("Select Game Mode")
        self.window.configure(bg="#1a1a2e")
        
        # Center window
        self.center_window()
        
        # Create canvas
        self.canvas = Canvas(self.window, bg="#1a1a2e", width=650, height=500, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=1)
        
        # Store button states and colors
        self.button_states = {}
        self.original_colors = {}
        
        self.create_mode_selection()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"650x500+{x}+{y}")
    
    def create_mode_selection(self):
        # Title with animation
        self.canvas.create_text(325, 50, text="SELECT GAME MODE", 
                              font=("Arial", 28, "bold"), 
                              fill="#4ecdc4", tags="title")
        
        # Mode buttons with better styling
        modes = [
            ("🎯 Classic Mode", "#2ecc71", "classic", "Traditional Ludo with standard rules"),
            ("⚡ Rush Mode", "#e67e22", "rush", "Fast-paced gameplay with quick turns"),
            ("🤝 Classic Team-Up", "#9b59b6", "team_up", "Classic mode with team partnerships")
        ]
        
        y_start = 120
        for i, (text, color, mode_id, description) in enumerate(modes):
            y = y_start + i * 90
            
            # Store original color
            self.original_colors[mode_id] = color
            
            # Create button container (invisible clickable area)
            container_rect = self.canvas.create_rectangle(80, y - 35, 570, y + 35,
                                                        fill="", outline="",
                                                        tags=f"{mode_id}_container")
            
            # Button background with gradient effect
            btn_bg = self.canvas.create_rectangle(100, y - 30, 550, y + 30,
                                                fill=color, outline="white", width=2,
                                                tags=f"{mode_id}_bg")
            
            # Button shadow for depth
            shadow = self.canvas.create_rectangle(103, y - 27, 553, y + 33,
                                                fill="#000000", outline="",
                                                tags=f"{mode_id}_shadow")
            self.canvas.tag_lower(f"{mode_id}_shadow")
            
            # Button text
            title_text = self.canvas.create_text(325, y - 8, text=text, 
                                               font=("Arial", 18, "bold"), 
                                               fill="white", tags=f"{mode_id}_title")
            
            # Description text
            desc_text = self.canvas.create_text(325, y + 12, text=description, 
                                              font=("Arial", 10, "italic"), 
                                              fill="#f0f0f0", tags=f"{mode_id}_desc")
            
            # Group all button elements
            button_tags = [f"{mode_id}_container", f"{mode_id}_bg", f"{mode_id}_shadow", 
                          f"{mode_id}_title", f"{mode_id}_desc"]
            
            # Bind events to all button elements
            for tag in button_tags:
                self.canvas.tag_bind(tag, "<Button-1>", lambda e, m=mode_id: self.select_mode(m))
                self.canvas.tag_bind(tag, "<Enter>", lambda e, m=mode_id: self.button_hover(m))
                self.canvas.tag_bind(tag, "<Leave>", lambda e, m=mode_id: self.button_leave(m))
        
        # Back button with better styling
        back_y = 420
        back_bg = self.canvas.create_rectangle(230, back_y - 20, 420, back_y + 20,
                                             fill="#e74c3c", outline="white", width=2,
                                             tags="back_bg")
        
        back_shadow = self.canvas.create_rectangle(233, back_y - 17, 423, back_y + 23,
                                                 fill="#000000", outline="",
                                                 tags="back_shadow")
        self.canvas.tag_lower("back_shadow")
        
        back_text = self.canvas.create_text(325, back_y, text="← BACK TO MENU", 
                                          font=("Arial", 14, "bold"), 
                                          fill="white", tags="back_text")
        
        # Store original back button color
        self.original_colors["back"] = "#e74c3c"
        
        # Bind back button events
        back_tags = ["back_bg", "back_shadow", "back_text"]
        for tag in back_tags:
            self.canvas.tag_bind(tag, "<Button-1>", self.go_back)
            self.canvas.tag_bind(tag, "<Enter>", lambda e: self.button_hover("back"))
            self.canvas.tag_bind(tag, "<Leave>", lambda e: self.button_leave("back"))
    
    def button_hover(self, button_id):
        if button_id == "classic":
            # Brighten classic button
            self.canvas.itemconfig(f"classic_bg", fill="#27ae60")
            # Add slight scale effect by adjusting coordinates
            coords = self.canvas.coords("classic_bg")
            self.canvas.coords("classic_bg", coords[0]-2, coords[1]-2, coords[2]+2, coords[3]+2)
            
        elif button_id == "rush":
            # Brighten rush button
            self.canvas.itemconfig("rush_bg", fill="#d35400")
            coords = self.canvas.coords("rush_bg")
            self.canvas.coords("rush_bg", coords[0]-2, coords[1]-2, coords[2]+2, coords[3]+2)
            
        elif button_id == "team_up":
            # Brighten team-up button
            self.canvas.itemconfig("team_up_bg", fill="#8e44ad")
            coords = self.canvas.coords("team_up_bg")
            self.canvas.coords("team_up_bg", coords[0]-2, coords[1]-2, coords[2]+2, coords[3]+2)
            
        elif button_id == "back":
            # Brighten back button
            self.canvas.itemconfig("back_bg", fill="#c0392b")
            coords = self.canvas.coords("back_bg")
            self.canvas.coords("back_bg", coords[0]-2, coords[1]-2, coords[2]+2, coords[3]+2)
    
    def button_leave(self, button_id):
        if button_id == "classic":
            # Restore original color and size
            self.canvas.itemconfig("classic_bg", fill=self.original_colors["classic"])
            self.canvas.coords("classic_bg", 100, 120-30, 550, 120+30)
            
        elif button_id == "rush":
            # Restore original color and size
            self.canvas.itemconfig("rush_bg", fill=self.original_colors["rush"])
            self.canvas.coords("rush_bg", 100, 210-30, 550, 210+30)
            
        elif button_id == "team_up":
            # Restore original color and size
            self.canvas.itemconfig("team_up_bg", fill=self.original_colors["team_up"])
            self.canvas.coords("team_up_bg", 100, 300-30, 550, 300+30)
            
        elif button_id == "back":
            # Restore original color and size
            self.canvas.itemconfig("back_bg", fill=self.original_colors["back"])
            self.canvas.coords("back_bg", 230, 400, 420, 440)
    
    def select_mode(self, mode):
        # Add selection animation
        self.animate_selection(mode)
        
    def animate_selection(self, mode):
        # Flash the selected button
        original_color = self.original_colors[mode]
        flash_color = "#ffffff"
        
        # Flash effect
        self.canvas.itemconfig(f"{mode}_bg", fill=flash_color)
        self.window.after(100, lambda: self.canvas.itemconfig(f"{mode}_bg", fill=original_color))
        self.window.after(200, lambda: self.canvas.itemconfig(f"{mode}_bg", fill=flash_color))
        self.window.after(300, lambda: self.canvas.itemconfig(f"{mode}_bg", fill=original_color))
        
        # Close window after animation
        self.window.after(500, lambda: self.complete_selection(mode))
    
    def complete_selection(self, mode):
        self.window.destroy()
        self.on_mode_selected(mode)
    
    def go_back(self, event):
        # Add closing animation
        self.canvas.create_text(325, 250, text="Returning to Main Menu...", 
                              font=("Arial", 16), fill="#4ecdc4", tags="closing_text")
        
        # Fade out effect
        self.window.after(500, self.close_and_return)
    
    def close_and_return(self):
        self.window.destroy()
        # Show the parent window again
        if self.parent_window:
            self.parent_window.deiconify()

class LudoFrontPage:
    def __init__(self, root):
        self.window = root
        self.window.geometry("800x630")
        self.window.maxsize(800, 630)
        self.window.minsize(800, 630)
        self.window.title("AI Ludo Game")
        try:
            _center_window(self.window, 800, 630)
        except Exception:
            pass
        
        # Handle window close event properly
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        try:
            self.window.iconbitmap("Images/ludo_icon.ico")
        except:
            print("Icon file not found, using default")
        
        # Create main canvas
        self.canvas = Canvas(self.window, bg="#1a1a2e", width=800, height=630, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=1)

        # Bind global click sound for all Tk Buttons in this window
        try:
            self.window.bind_class('Button', '<Button-1>', lambda e: self._play_click_sound(), add='+')
        except Exception:
            pass
        
        # Animation variables
        self.animation_step = 0
        self.dice_rotation = 0
        self.color_shift = 0
        
        # Create background elements
        self.create_background()
        
        # Create title
        self.create_title()
        
        # Create animated dice
        self.create_dice()
        
        # Create buttons
        self.create_buttons()
        
        # Create game pieces decoration
        self.create_game_pieces()
        
        # Start animations
        self.animate()
    
    def create_background(self):
        # Create gradient background effect with rectangles
        for i in range(50):
            color_intensity = int(26 + (46 - 26) * (i / 50))
            color = f"#{color_intensity:02x}{color_intensity + 10:02x}{color_intensity + 20:02x}"
            self.canvas.create_rectangle(0, i * 13, 800, (i + 1) * 13, 
                                       fill=color, outline=color)
        
        # Add decorative stars
        for _ in range(30):
            x = random.randint(0, 800)
            y = random.randint(0, 630)
            size = random.randint(2, 6)
            self.canvas.create_oval(x, y, x + size, y + size, 
                                  fill="white", outline="white")
    
    def create_title(self):
        # Main title "LUDO"
        self.canvas.create_text(400, 150, text="LUDO", 
                              font=("Arial", 72, "bold"), 
                              fill="#ff6b6b", tags="title")
        
        # Subtitle "GAME"
        self.canvas.create_text(400, 210, text="GAME", 
                              font=("Arial", 48, "bold"), 
                              fill="#4ecdc4", tags="subtitle")
        
        # AI Integration text
        self.canvas.create_text(400, 260, text="WITH AI INTEGRATION", 
                              font=("Arial", 16, "italic"), 
                              fill="#ffd700", tags="ai_text")
        
        # Add glow effect to title
        self.canvas.create_text(402, 152, text="LUDO", 
                              font=("Arial", 72, "bold"), 
                              fill="#ff4444", tags="title_shadow")
        self.canvas.tag_lower("title_shadow")
    
    def create_dice(self):
        # Create animated dice
        self.dice_positions = [(250, 320), (550, 320)]
        self.dice_objects = []
        
        for i, (x, y) in enumerate(self.dice_positions):
            dice_bg = self.canvas.create_rectangle(x - 25, y - 25, x + 25, y + 25,
                                                 fill="white", outline="#333", width=3,
                                                 tags=f"dice_{i}")
            
            # Create dice dots
            dots = self.create_dice_dots(x, y, random.randint(1, 6), i)
            self.dice_objects.append((dice_bg, dots))
    
    def create_dice_dots(self, x, y, number, dice_id):
        dots = []
        dot_positions = {
            1: [(0, 0)],
            2: [(-10, -10), (10, 10)],
            3: [(-10, -10), (0, 0), (10, 10)],
            4: [(-10, -10), (10, -10), (-10, 10), (10, 10)],
            5: [(-10, -10), (10, -10), (0, 0), (-10, 10), (10, 10)],
            6: [(-10, -10), (10, -10), (-10, 0), (10, 0), (-10, 10), (10, 10)]
        }
        
        for dx, dy in dot_positions[number]:
            dot = self.canvas.create_oval(x + dx - 3, y + dy - 3, 
                                        x + dx + 3, y + dy + 3,
                                        fill="black", tags=f"dice_dot_{dice_id}")
            dots.append(dot)
        
        return dots
    
    def create_buttons(self):
        # Play button
        play_btn_bg = self.canvas.create_rectangle(300, 360, 500, 400,
                                                 fill="#2ecc71", outline="#27ae60", width=3,
                                                 tags="play_btn")
        self.canvas.create_text(400, 380, text="PLAY GAME", 
                              font=("Arial", 18, "bold"), 
                              fill="white", tags="play_btn")
        
        # Game Modes button
        modes_btn_bg = self.canvas.create_rectangle(300, 420, 500, 460,
                                                  fill="#9b59b6", outline="#8e44ad", width=3,
                                                  tags="modes_btn")
        self.canvas.create_text(400, 440, text="GAME MODES", 
                              font=("Arial", 16, "bold"), 
                              fill="white", tags="modes_btn")
        
        # Instructions button
        inst_btn_bg = self.canvas.create_rectangle(300, 480, 500, 520,
                                                 fill="#3498db", outline="#2980b9", width=3,
                                                 tags="inst_btn")
        self.canvas.create_text(400, 500, text="INSTRUCTIONS", 
                              font=("Arial", 14, "bold"), 
                              fill="white", tags="inst_btn")
        
        # Exit button
        exit_btn_bg = self.canvas.create_rectangle(300, 540, 500, 580,
                                                 fill="#e74c3c", outline="#c0392b", width=3,
                                                 tags="exit_btn")
        self.canvas.create_text(400, 560, text="EXIT", 
                              font=("Arial", 14, "bold"), 
                              fill="white", tags="exit_btn")
        
        # Bind click events
        self.canvas.tag_bind("play_btn", "<Button-1>", self.start_game)
        self.canvas.tag_bind("modes_btn", "<Button-1>", self.show_game_modes)
        self.canvas.tag_bind("inst_btn", "<Button-1>", self.show_instructions)
        self.canvas.tag_bind("exit_btn", "<Button-1>", self.exit_game)
        
        # Add hover effects
        self.canvas.tag_bind("play_btn", "<Enter>", lambda e: self.button_hover("play"))
        self.canvas.tag_bind("play_btn", "<Leave>", lambda e: self.button_leave("play"))
        self.canvas.tag_bind("modes_btn", "<Enter>", lambda e: self.button_hover("modes"))
        self.canvas.tag_bind("modes_btn", "<Leave>", lambda e: self.button_leave("modes"))
        self.canvas.tag_bind("inst_btn", "<Enter>", lambda e: self.button_hover("inst"))
        self.canvas.tag_bind("inst_btn", "<Leave>", lambda e: self.button_leave("inst"))
        self.canvas.tag_bind("exit_btn", "<Enter>", lambda e: self.button_hover("exit"))
        self.canvas.tag_bind("exit_btn", "<Leave>", lambda e: self.button_leave("exit"))
    
    def create_game_pieces(self):
        # Create colorful game pieces around the screen
        colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24"]
        positions = [(100, 100), (700, 100), (100, 530), (700, 530)]
        
        for i, ((x, y), color) in enumerate(zip(positions, colors)):
            # Create piece
            piece = self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15,
                                          fill=color, outline="white", width=2,
                                          tags=f"piece_{i}")
            # Create number on piece
            self.canvas.create_text(x, y, text=str(i + 1), 
                                  font=("Arial", 12, "bold"), 
                                  fill="white", tags=f"piece_num_{i}")
    
    def animate(self):
        # Animate title glow effect
        self.color_shift += 0.1
        glow_intensity = int(100 + 50 * math.sin(self.color_shift))
        glow_color = f"#ff{glow_intensity:02x}{glow_intensity:02x}"
        
        # Update title color
        items = self.canvas.find_withtag("title")
        if items:
            colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#f9ca24"]
            color_index = int(self.color_shift * 2) % len(colors)
            self.canvas.itemconfig(items[0], fill=colors[color_index])
        
        # Animate dice
        self.dice_rotation += 1
        if self.dice_rotation % 60 == 0:  # Change dice every 60 frames (about 1 second)
            for i, (dice_bg, dots) in enumerate(self.dice_objects):
                # Remove old dots
                for dot in dots:
                    self.canvas.delete(dot)
                
                # Create new dots
                x, y = self.dice_positions[i]
                new_dots = self.create_dice_dots(x, y, random.randint(1, 6), i)
                self.dice_objects[i] = (dice_bg, new_dots)
        
        # Animate game pieces (floating effect)
        for i in range(4):
            offset_y = 5 * math.sin(self.animation_step + i * math.pi / 2)
            items = self.canvas.find_withtag(f"piece_{i}")
            if items:
                coords = self.canvas.coords(items[0])
                if len(coords) == 4:
                    x1, y1, x2, y2 = coords
                    center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
                    # Reset position first
                    positions = [(100, 100), (700, 100), (100, 530), (700, 530)]
                    base_x, base_y = positions[i]
                    new_y = base_y + offset_y
                    
                    self.canvas.coords(items[0], base_x - 15, new_y - 15, 
                                     base_x + 15, new_y + 15)
                    
                    # Update number position too
                    num_items = self.canvas.find_withtag(f"piece_num_{i}")
                    if num_items:
                        self.canvas.coords(num_items[0], base_x, new_y)
        
        self.animation_step += 0.1
        
        # Schedule next animation frame
        self.window.after(50, self.animate)
    
    def button_hover(self, button_type):
        if button_type == "play":
            items = self.canvas.find_withtag("play_btn")
            if items:
                for item in items:
                    if self.canvas.type(item) == "rectangle":
                        self.canvas.itemconfig(item, fill="#27ae60")
        elif button_type == "modes":
            items = self.canvas.find_withtag("modes_btn")
            if items:
                for item in items:
                    if self.canvas.type(item) == "rectangle":
                        self.canvas.itemconfig(item, fill="#8e44ad")
        elif button_type == "inst":
            items = self.canvas.find_withtag("inst_btn")
            if items:
                for item in items:
                    if self.canvas.type(item) == "rectangle":
                        self.canvas.itemconfig(item, fill="#2980b9")
        elif button_type == "exit":
            items = self.canvas.find_withtag("exit_btn")
            if items:
                for item in items:
                    if self.canvas.type(item) == "rectangle":
                        self.canvas.itemconfig(item, fill="#c0392b")
    
    def button_leave(self, button_type):
        if button_type == "play":
            items = self.canvas.find_withtag("play_btn")
            if items:
                for item in items:
                    if self.canvas.type(item) == "rectangle":
                        self.canvas.itemconfig(item, fill="#2ecc71")
        elif button_type == "modes":
            items = self.canvas.find_withtag("modes_btn")
            if items:
                for item in items:
                    if self.canvas.type(item) == "rectangle":
                        self.canvas.itemconfig(item, fill="#9b59b6")
        elif button_type == "inst":
            items = self.canvas.find_withtag("inst_btn")
            if items:
                for item in items:
                    if self.canvas.type(item) == "rectangle":
                        self.canvas.itemconfig(item, fill="#3498db")
        elif button_type == "exit":
            items = self.canvas.find_withtag("exit_btn")
            if items:
                for item in items:
                    if self.canvas.type(item) == "rectangle":
                        self.canvas.itemconfig(item, fill="#e74c3c")
    
    def start_game(self, event):
        # Add button press animation
        self.animate_button_press("play")
        # Close front page and start the main game after animation
        self.window.after(300, lambda: self.close_and_start_game())
    
    def close_and_start_game(self):
        try:
            stop_theme_music()
        except Exception:
            pass
        self.window.destroy()
        # Start original Classic Ludo directly
        self.start_classic_game()
    
    def show_game_modes(self, event):
        # Add button press animation
        self.animate_button_press("modes")
        # Show game mode selection after animation
        self.window.after(300, lambda: self.open_mode_selection())
    
    def open_mode_selection(self):
        self.window.withdraw()  # Hide current window
        mode_window = Toplevel()
        GameModeSelector(mode_window, self.on_mode_selected, self.window)  # Pass parent window
    
    def animate_button_press(self, button_type):
        # Create a flash effect for button press
        items = self.canvas.find_withtag(f"{button_type}_btn")
        if items:
            for item in items:
                if self.canvas.type(item) == "rectangle":
                    # Flash white briefly
                    self.canvas.itemconfig(item, fill="white")
                    # Return to hover color after 150ms
                    if button_type == "play":
                        self.window.after(150, lambda: self.canvas.itemconfig(item, fill="#27ae60"))
                    elif button_type == "modes":
                        self.window.after(150, lambda: self.canvas.itemconfig(item, fill="#8e44ad"))
    
    def on_mode_selected(self, mode):
        # Handle mode selection
        print(f"Selected mode: {mode}")
        self.window.deiconify()  # Show main window again
        try:
            stop_theme_music()
        except Exception:
            pass
        self.window.destroy()
        
        # Start game with selected mode
        if mode == "classic":
            print("Starting Classic Mode...")
            # Initialize your main game with classic rules
            self.start_classic_game()
        elif mode == "rush":
            print("Starting Rush Mode...")
            # Initialize your main game with rush rules
            self.start_rush_game()
        elif mode == "team_up":
            print("Starting Classic Team-Up Mode...")
            # Initialize your main game with team-up rules
            self.start_team_up_game()
    
    def start_classic_game(self):
        """Start the classic Ludo game"""
        try:
            # Import and start the original Ludo game
            from Ludo_game_with_Sam import Ludo
            import sys
            import os
            from tkinter.simpledialog import askstring
            
            # Create new window for classic game
            game_window = Tk()
            game_window.geometry("800x630")
            game_window.maxsize(800,630)
            game_window.minsize(800,630)
            game_window.title("Classic Ludo Game")
            game_window.iconbitmap("Images/ludo_icon.ico")
            
            try:
                _center_window(game_window, 800, 630)
            except Exception:
                pass
            
            # Load dice images
            from PIL import Image, ImageTk
            try:
                # Try new PIL version first
                block_six_side = ImageTk.PhotoImage(Image.open("Images/6_block.png").resize((33, 33), Image.LANCZOS))
                block_five_side = ImageTk.PhotoImage(Image.open("Images/5_block.png").resize((33, 33), Image.LANCZOS))
                block_four_side = ImageTk.PhotoImage(Image.open("Images/4_block.png").resize((33, 33), Image.LANCZOS))
                block_three_side = ImageTk.PhotoImage(Image.open("Images/3_block.png").resize((33, 33), Image.LANCZOS))
                block_two_side = ImageTk.PhotoImage(Image.open("Images/2_block.png").resize((33, 33), Image.LANCZOS))
                block_one_side = ImageTk.PhotoImage(Image.open("Images/1_block.png").resize((33, 33), Image.LANCZOS))
            except AttributeError:
                # Fallback for older PIL versions
                block_six_side = ImageTk.PhotoImage(Image.open("Images/6_block.png").resize((33, 33), Image.ANTIALIAS))
                block_five_side = ImageTk.PhotoImage(Image.open("Images/5_block.png").resize((33, 33), Image.ANTIALIAS))
                block_four_side = ImageTk.PhotoImage(Image.open("Images/4_block.png").resize((33, 33), Image.ANTIALIAS))
                block_three_side = ImageTk.PhotoImage(Image.open("Images/3_block.png").resize((33, 33), Image.ANTIALIAS))
                block_two_side = ImageTk.PhotoImage(Image.open("Images/2_block.png").resize((33, 33), Image.ANTIALIAS))
                block_one_side = ImageTk.PhotoImage(Image.open("Images/1_block.png").resize((33, 33), Image.ANTIALIAS))
            
            # Do NOT ask for names here; let the game ask after Play-With selection

            # Start the classic game
            game = Ludo(game_window, block_six_side, block_five_side, block_four_side, block_three_side, block_two_side, block_one_side)
            game_window.mainloop()
            
        except Exception as e:
            print(f"Error starting classic game: {e}")
            messagebox.showerror("Error", "Could not start Classic Mode. Please check if Ludo_game_with_Sam.py exists.")
    
    def start_rush_game(self):
        """Start the rush mode game"""
        try:
            # Stop any running animations to prevent conflicts
            try:
                self.window.after_cancel("all")
            except:
                pass

            # Import and start the Rush Mode game
            from Ludo_RushMode import LudoRush
            # Create new window for rush game
            game_window = Tk()
            game_window.geometry("800x630")
            game_window.maxsize(800,630)
            game_window.minsize(800,630)
            game_window.title("Ludo Rush Mode")
            try:
                game_window.iconbitmap("Images/ludo_icon.ico")
            except:
                pass
            
            try:
                _center_window(game_window, 800, 630)
            except Exception:
                pass

            # Load dice images
            from PIL import Image, ImageTk
            try:
                block_six_side = ImageTk.PhotoImage(Image.open("Images/6_block.png").resize((33, 33), Image.LANCZOS))
                block_five_side = ImageTk.PhotoImage(Image.open("Images/5_block.png").resize((33, 33), Image.LANCZOS))
                block_four_side = ImageTk.PhotoImage(Image.open("Images/4_block.png").resize((33, 33), Image.LANCZOS))
                block_three_side = ImageTk.PhotoImage(Image.open("Images/3_block.png").resize((33, 33), Image.LANCZOS))
                block_two_side = ImageTk.PhotoImage(Image.open("Images/2_block.png").resize((33, 33), Image.LANCZOS))
                block_one_side = ImageTk.PhotoImage(Image.open("Images/1_block.png").resize((33, 33), Image.LANCZOS))
            except AttributeError:
                block_six_side = ImageTk.PhotoImage(Image.open("Images/6_block.png").resize((33, 33), Image.ANTIALIAS))
                block_five_side = ImageTk.PhotoImage(Image.open("Images/5_block.png").resize((33, 33), Image.ANTIALIAS))
                block_four_side = ImageTk.PhotoImage(Image.open("Images/4_block.png").resize((33, 33), Image.ANTIALIAS))
                block_three_side = ImageTk.PhotoImage(Image.open("Images/3_block.png").resize((33, 33), Image.ANTIALIAS))
                block_two_side = ImageTk.PhotoImage(Image.open("Images/2_block.png").resize((33, 33), Image.ANTIALIAS))
                block_one_side = ImageTk.PhotoImage(Image.open("Images/1_block.png").resize((33, 33), Image.ANTIALIAS))

            # Start the Rush Mode game
            game = LudoRush(game_window, block_six_side, block_five_side, block_four_side, block_three_side, block_two_side, block_one_side)
            game_window.mainloop()

        except Exception as e:
            print(f"Error starting rush game: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Could not start Rush Mode.\nError: {str(e)}")
    
    def start_team_up_game(self):
        """Start the team-up Ludo game"""
        try:
            # Stop any running animations to prevent conflicts
            try:
                self.window.after_cancel("all")
            except:
                pass
            
            # Import and start the team-up Ludo game
            from Ludo_TeamUp_Cosmic import LudoTeamUp
            import sys
            import os
            
            # Create new window for team-up game
            game_window = Tk()
            game_window.geometry("800x630")
            game_window.maxsize(800,630)
            game_window.minsize(800,630)
            game_window.title("Team-Up Ludo - Cosmic Theme")
            try:
                game_window.iconbitmap("Images/ludo_icon.ico")
            except:
                pass  # Icon not critical
            
            try:
                _center_window(game_window, 800, 630)
            except Exception:
                pass  # Centering not critical either
            
            # Load dice images
            from PIL import Image, ImageTk
            try:
                # Try new PIL version first
                block_six_side = ImageTk.PhotoImage(Image.open("Images/6_block.png").resize((33, 33), Image.LANCZOS))
                block_five_side = ImageTk.PhotoImage(Image.open("Images/5_block.png").resize((33, 33), Image.LANCZOS))
                block_four_side = ImageTk.PhotoImage(Image.open("Images/4_block.png").resize((33, 33), Image.LANCZOS))
                block_three_side = ImageTk.PhotoImage(Image.open("Images/3_block.png").resize((33, 33), Image.LANCZOS))
                block_two_side = ImageTk.PhotoImage(Image.open("Images/2_block.png").resize((33, 33), Image.LANCZOS))
                block_one_side = ImageTk.PhotoImage(Image.open("Images/1_block.png").resize((33, 33), Image.LANCZOS))
            except AttributeError:
                # Fallback for older PIL versions
                block_six_side = ImageTk.PhotoImage(Image.open("Images/6_block.png").resize((33, 33), Image.ANTIALIAS))
                block_five_side = ImageTk.PhotoImage(Image.open("Images/5_block.png").resize((33, 33), Image.ANTIALIAS))
                block_four_side = ImageTk.PhotoImage(Image.open("Images/4_block.png").resize((33, 33), Image.ANTIALIAS))
                block_three_side = ImageTk.PhotoImage(Image.open("Images/3_block.png").resize((33, 33), Image.ANTIALIAS))
                block_two_side = ImageTk.PhotoImage(Image.open("Images/2_block.png").resize((33, 33), Image.ANTIALIAS))
                block_one_side = ImageTk.PhotoImage(Image.open("Images/1_block.png").resize((33, 33), Image.ANTIALIAS))
            
            # Do NOT ask for names/team here; let the game ask after Play-With selection

            # Start the team-up game
            game = LudoTeamUp(game_window, block_six_side, block_five_side, block_four_side, block_three_side, block_two_side, block_one_side)
            try:
                # Apply default team names if supported
                if hasattr(game, 'set_team_names'):
                    game.set_team_names("Team Alpha", "Team Beta")
            except Exception:
                pass
            game_window.mainloop()
            
        except Exception as e:
            print(f"Error starting team-up game: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Could not start Team-Up Mode.\nError: {str(e)}")
    
    def show_instructions(self, event):
        instructions = """
        LUDO GAME INSTRUCTIONS:

        CLASSIC MODE:
        1. Each player has 4 tokens that start in their home base
        2. Roll a 6 to move a token out of home base
        3. Move tokens clockwise around the board
        4. Land on an opponent's token to send it back home
        5. Safe squares (with stars) protect your tokens
        6. Get all 4 tokens to the center to win!
        
        TEAM-UP MODE (NEW!):
        - Team Alpha: Red + Green players work together
        - Team Beta: Yellow + Blue players work together
        - Teams win when BOTH players get all their tokens home
        - Cosmic theme with beautiful space colors
        - Team scoring system tracks victories
        
        AI FEATURES:
        - Play against computer opponent
        - Smart AI decision making
        - Adaptive difficulty
        
        GAME MODES:
        - Classic Mode: Traditional Ludo with standard rules
        - Rush Mode: Fast-paced gameplay (coming soon)
        - Classic Team-Up: Team-based gameplay with cosmic theme
        
        Click PLAY GAME to start Classic Mode directly!
        Click GAME MODES to choose Team-Up mode!
        """
        messagebox.showinfo("Game Instructions", instructions)
    
    def exit_game(self, event):
        if messagebox.askquestion("Exit", "Are you sure you want to exit?") == "yes":
            self.on_closing()
    
    def on_closing(self):
        """Properly close the application"""
        try:
            self.window.quit()
            self.window.destroy()
        except:
            pass

    def _play_click_sound(self):
        # Reuse base helper if available after game starts; otherwise lightweight local caller
        def _play():
            try:
                try:
                    from playsound import playsound
                    playsound("sounds/computer-mouse-click-02-383961.mp3", block=False)
                    return
                except Exception:
                    pass
                try:
                    import winsound  # type: ignore
                    winsound.PlaySound("sounds/Jump.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                    return
                except Exception:
                    pass
            except Exception:
                pass
        try:
            threading.Thread(target=_play, daemon=True).start()
        except Exception:
            pass

def start_main_menu():
    main_window = Tk()
    front_page = LudoFrontPage(main_window)
    main_window.mainloop()

def main():
    # Show splash screen first
    splash_window = Tk()
    splash_screen = SplashScreen(splash_window, start_main_menu)
    splash_window.mainloop()

# To integrate with your existing game:
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("Falling back to main menu...")
        start_main_menu()