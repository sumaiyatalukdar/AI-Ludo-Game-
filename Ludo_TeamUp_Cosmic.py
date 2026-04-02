from tkinter import messagebox
from Ludo_game_with_Sam import Ludo
import tkinter as tk
from typing import Dict, Set, List, Optional, Tuple
import random
from enum import Enum


class Team(Enum):
    ALPHA = "alpha"
    BETA = "beta"


class AIStrategy(Enum):
    RANDOM = "random"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    SMART = "smart"


class LudoTeamUp(Ludo):
    """Enhanced team-based Ludo game with improved AI, animations, and user experience."""
    
    def __init__(self, root, six_side_block, five_side_block, four_side_block, 
                 three_side_block, two_side_block, one_side_block):
        # Team configuration
        self.team_alpha: Set[str] = {"red", "yellow"}
        self.team_beta: Set[str] = {"sky_blue", "green"}
        self.team_mapping = {
            "red": Team.ALPHA, "yellow": Team.ALPHA,
            "sky_blue": Team.BETA, "green": Team.BETA
        }
        
        # Game state
        self.finished_colors: Set[str] = set()
        self.alpha_wins: int = 0
        self.beta_wins: int = 0
        self.game_stats = {
            "moves_played": 0,
            "captures_made": 0,
            "sixes_rolled": 0,
            "game_duration": 0
        }
        
        # UI elements
        self._ui_elements = {
            "turn_text_id": None,
            "alpha_score_id": None,
            "beta_score_id": None,
            "subtitle_id": None,
            "alpha_name_id": None,
            "beta_name_id": None,
            "turn_bg_id": None,
            "status_panel_id": None
        }
        self._team_status_elements: Dict = {}
        
        # Team names and customization
        self.team_names = {"alpha": "Team Alpha", "beta": "Team Beta"}
        self.team_colors = {
            Team.ALPHA: {"primary": "#dc2626", "secondary": "#fca5a5"},
            Team.BETA: {"primary": "#0ea5e9", "secondary": "#7dd3fc"}
        }
        
        # AI configuration
        self.ai_strategy = AIStrategy.SMART
        self.ai_team_colors: Set[str] = set()
        self.is_teamup_vs_computer: bool = False
        
        # Animation and effects
        self._animation_queue = []
        self._celebration_active = False
        
        super().__init__(root, six_side_block, five_side_block, four_side_block, 
                        three_side_block, two_side_block, one_side_block)
        
        # Prefer classic board UI unless explicitly enabled
        self.use_classic_ui = True
        self._initialize_team_game()

    def _enforce_vs_computer_turn_order(self):
        """Keep turns in the fixed order: Red (H), Sky Blue (AI), Yellow (H), Green (AI)."""
        try:
            if not self.is_teamup_vs_computer:
                return
            desired = [0, 1, 2, 3]  # 0=red,1=sky_blue,2=yellow,3=green
            # Keep only players still in rotation, but in the desired order
            current = set(self.total_people_play or [])
            self.total_people_play = [i for i in desired if i in current]
            # Clamp time_for if it went out of bounds
            if getattr(self, 'time_for', -1) >= len(self.total_people_play):
                self.time_for = -1
        except Exception:
            pass

    def _get_positions_and_dice(self, color: str):
        """Return (positions_list, dice_value) for given color from base game state."""
        try:
            color = color.lower()
            positions_map = {
                "red": self.red_coin_position,
                "sky_blue": self.sky_blue_coin_position,
                "yellow": self.yellow_coin_position,
                "green": self.green_coin_position,
            }
            dice_map = {
                "red": self.move_red_counter,
                "sky_blue": self.move_sky_blue_counter,
                "yellow": self.move_yellow_counter,
                "green": self.move_green_counter,
            }
            return positions_map.get(color, [-1, -1, -1, -1]), dice_map.get(color, 0)
        except Exception:
            return [-1, -1, -1, -1], 0

    def _initialize_team_game(self):
        """Initialize all team-specific features and UI elements."""
        try:
            if not getattr(self, 'use_classic_ui', False):
                self._apply_enhanced_team_theme()
                self._create_team_status_panels()
                self._update_team_turn_banner()
                self._rename_base_player_labels()
            # Always enforce gameplay rules and shortcuts
            self._enforce_teamup_players()
            self._setup_keyboard_shortcuts()
        except Exception as e:
            print(f"Initialization error: {e}")

    def take_initial_control(self):
        """Enhanced initial control with better UI and options."""
        self._disable_all_predict_buttons()
        
        top = tk.Toplevel()
        self._setup_mode_selection_window(top)
        
        # Add AI difficulty selection for vs computer mode
        self._add_ai_difficulty_selection(top)
        
        # Enhanced button styling and functionality
        self._create_mode_buttons(top)
        
        top.grab_set()
        top.focus_set()

    def _setup_mode_selection_window(self, window):
        """Setup the mode selection window with enhanced styling."""
        window.geometry("600x350")
        window.maxsize(600, 350)
        window.minsize(600, 350)
        window.config(bg="#0a0a0a")
        window.title("🏆 Team-Up Ludo - Game Mode")
        
        try:
            window.iconbitmap("Images/ludo_icon.ico")
        except Exception:
            pass
        
        # Enhanced header with gradient effect
        header = tk.Label(window, text="⚔️ TEAM-UP BATTLE MODE ⚔️", 
                         font=("Arial Black", 22, "bold"), 
                         bg="#0a0a0a", fg="#fbbf24")
        header.place(x=80, y=30)
        
        # Game info with better formatting
        info_text = "• Exactly 4 players in 2 teams\n• Team Alpha: Red + Yellow\n• Team Beta: Sky Blue + Green"
        info_label = tk.Label(window, text=info_text, font=("Arial", 12, "bold"), 
                             bg="#0a0a0a", fg="#cbd5e1", justify=tk.LEFT)
        info_label.place(x=150, y=80)

    def _add_ai_difficulty_selection(self, parent):
        """Add AI difficulty selection for computer mode."""
        difficulty_frame = tk.Frame(parent, bg="#0a0a0a")
        difficulty_frame.place(x=150, y=150)
        
        tk.Label(difficulty_frame, text="AI Difficulty:", 
                font=("Arial", 12, "bold"), bg="#0a0a0a", fg="#ffffff").pack(anchor="w")
        
        self.ai_difficulty_var = tk.StringVar(value="smart")
        
        difficulties = [
            ("Beginner", "random", "#10b981"),
            ("Intermediate", "defensive", "#f59e0b"), 
            ("Advanced", "aggressive", "#ef4444"),
            ("Expert", "smart", "#8b5cf6")
        ]
        
        for text, value, color in difficulties:
            rb = tk.Radiobutton(difficulty_frame, text=text, variable=self.ai_difficulty_var,
                               value=value, font=("Arial", 10), bg="#0a0a0a", 
                               fg=color, selectcolor="#1f2937", 
                               activebackground="#0a0a0a", activeforeground=color)
            rb.pack(anchor="w")

    def _create_mode_buttons(self, parent):
        """Create enhanced mode selection buttons."""
        button_config = {
            "font": ("Arial Black", 16, "bold"),
            "relief": tk.RAISED,
            "bd": 3,
            "width": 16,
            "height": 2,
            "activebackground": "#1f2937"
        }
        
        # Computer mode button with enhanced styling
        computer_btn = tk.Button(parent, text="🤖 vs Computer", 
                                bg="#1f2937", fg="#10b981",
                                command=self._start_vs_computer,
                                **button_config)
        computer_btn.place(x=80, y=250)
        
        # Friends mode button
        friends_btn = tk.Button(parent, text="👥 vs Friends", 
                               bg="#1f2937", fg="#3b82f6",
                               command=self._start_with_friends,
                               **button_config)
        friends_btn.place(x=320, y=250)
        
        # Add hover effects
        self._add_button_hover_effects([computer_btn, friends_btn])

    def _add_button_hover_effects(self, buttons):
        """Add hover effects to buttons."""
        def on_enter(e, original_bg):
            e.widget.config(bg="#374151")
            
        def on_leave(e, original_bg):
            e.widget.config(bg=original_bg)
        
        for btn in buttons:
            original_bg = btn.cget("bg")
            btn.bind("<Enter>", lambda e, bg=original_bg: on_enter(e, bg))
            btn.bind("<Leave>", lambda e, bg=original_bg: on_leave(e, bg))

    def _start_vs_computer(self):
        """Start game against computer with selected difficulty."""
        try:
            # Set AI strategy based on selection
            strategy_mapping = {
                "random": AIStrategy.RANDOM,
                "defensive": AIStrategy.DEFENSIVE,
                "aggressive": AIStrategy.AGGRESSIVE,
                "smart": AIStrategy.SMART
            }
            self.ai_strategy = strategy_mapping.get(
                getattr(self, 'ai_difficulty_var', tk.StringVar()).get(), 
                AIStrategy.SMART
            )
            
            # Disable base single-robot mode; we run team-based AI ourselves
            self.robo_prem = 0
            self.is_teamup_vs_computer = True
            self.ai_team_colors = set(self.team_beta)
            self.total_people_play = [0, 1, 2, 3]
            self._enforce_vs_computer_turn_order()
            
            # Pre-assign fixed bot names for computer team
            try:
                self.player_names[1] = "bot1"  # Sky Blue
                self.player_names[3] = "bot2"  # Green
            except Exception:
                pass
            self._ask_player_names(num_players=4, vs_computer=True)
            self._close_mode_selection_window()
            self._start_game()
            
        except Exception as e:
            print(f"Computer mode start error: {e}")

    def _start_with_friends(self):
        """Start game with friends."""
        try:
            self.robo_prem = 0
            self.is_teamup_vs_computer = False
            self.ai_team_colors = set()
            self.total_people_play = [0, 1, 2, 3]
            
            self._ask_player_names(num_players=4, vs_computer=False)
            self._close_mode_selection_window()
            self._start_game()
            
        except Exception as e:
            print(f"Friends mode start error: {e}")

    def _close_mode_selection_window(self):
        """Close the mode selection window."""
        for widget in self.window.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
                break

    def _start_game(self):
        """Initialize and start the game."""
        self.time_for = -1
        self.make_command()
        self._show_game_start_message()

    def _show_game_start_message(self):
        """Show enhanced game start message."""
        start_msg = f"🏆 TEAM BATTLE BEGINS! 🏆\n\n"
        start_msg += f"{self.team_names['alpha']} vs {self.team_names['beta']}\n\n"
        if self.is_teamup_vs_computer:
            start_msg += f"AI Difficulty: {self.ai_strategy.value.title()}\n"
        start_msg += "May the best team win!"
        
        messagebox.showinfo("Game Started! 🎮", start_msg)

    def _disable_all_predict_buttons(self):
        """Disable all predict buttons safely."""
        for i in range(4):
            try:
                if hasattr(self, 'block_value_predict') and len(self.block_value_predict) > i:
                    self.block_value_predict[i][1]['state'] = 'disabled'
            except (IndexError, KeyError, AttributeError):
                pass

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for better UX."""
        try:
            self.window.bind('<space>', lambda e: self._handle_spacebar())
            self.window.bind('<r>', lambda e: self._restart_game())
            self.window.bind('<h>', lambda e: self._show_help())
            self.window.focus_set()
        except Exception as e:
            print(f"Keyboard setup error: {e}")

    def _handle_spacebar(self):
        """Handle spacebar press for current player's turn."""
        try:
            if self.time_for >= 0 and self.time_for < len(self.total_people_play):
                current_player_idx = self.total_people_play[self.time_for]
                if current_player_idx < len(self.block_value_predict):
                    button = self.block_value_predict[current_player_idx][1]
                    if button['state'] == 'normal':
                        button.invoke()
        except Exception as e:
            print(f"Spacebar handler error: {e}")

    def _show_help(self):
        """Show help dialog with controls and rules."""
        help_text = """🎮 TEAM-UP LUDO CONTROLS & RULES

🎯 OBJECTIVE:
Get both team members' tokens to the finish line first!

⌨️ KEYBOARD SHORTCUTS:
• SPACE - Roll dice for current player
• R - Restart game  
• H - Show this help

🤝 TEAM RULES:
• Team Alpha: Red + Yellow players
• Team Beta: Sky Blue + Green players
• Teammates can share spaces safely
• Team wins when both members finish

🎲 GAME TIPS:
• Protect teammates when possible
• Block opponents strategically
• Use 6s to get new tokens out
• Plan moves as a team!"""
        
        messagebox.showinfo("🎮 Game Help", help_text)

    def _restart_game(self):
        """Restart the current game with confirmation."""
        if messagebox.askyesno("🔄 Restart Game", "Are you sure you want to restart the current game?"):
            try:
                # Reset game state
                self.finished_colors.clear()
                self.game_stats = {k: 0 for k in self.game_stats}
                
                # Reset positions (this would need to be implemented in base class)
                # self._reset_all_positions()
                
                self.take_initial_control()
            except Exception as e:
                print(f"Restart error: {e}")

    def get_team_for_color(self, color: str) -> Team:
        """Get the team for a given color."""
        return self.team_mapping.get(color, Team.ALPHA)

    def get_teammate_color(self, color: str) -> Optional[str]:
        """Get the teammate's color for a given color."""
        if color in self.team_alpha:
            return next((c for c in self.team_alpha if c != color), None)
        elif color in self.team_beta:
            return next((c for c in self.team_beta if c != color), None)
        return None

    def _legal_moves_for(self, color: str) -> List[int]:
        """Enhanced legal move calculation with better validation."""
        try:
            positions, dice = self._get_positions_and_dice(color)
            legal = []
            
            for coin_idx in range(1, 5):
                pos = positions[coin_idx - 1]
                
                # Token not yet started
                if pos == -1:
                    if dice == 6:
                        legal.append(coin_idx)
                    continue
                
                # Token in home stretch (positions 100+)
                if pos >= 100:
                    if pos + dice <= 106:  # Can't overshoot finish
                        legal.append(coin_idx)
                # Token on main track
                else:
                    new_pos = pos + dice
                    # Handle wrapping around the board
                    if new_pos > 52:
                        new_pos = new_pos - 52
                    
                    # Check if move would put token in valid position
                    if self._is_valid_move(color, coin_idx, pos, new_pos):
                        legal.append(coin_idx)
            
            return legal
            
        except Exception as e:
            print(f"Legal moves calculation error for {color}: {e}")
            return []

    def _is_valid_move(self, color: str, coin_idx: int, current_pos: int, new_pos: int) -> bool:
        """Check if a move is valid considering game rules."""
        try:
            # Basic validation
            if new_pos < 0 or new_pos > 106:
                return False
            
            # Check for teammate stacking (allowed)
            teammate_color = self.get_teammate_color(color)
            if teammate_color and self._position_occupied_by_color(new_pos, teammate_color):
                return True  # Can stack with teammate
            
            # Check for opponent blocking (need to capture or find alternative)
            for opponent_color in ["red", "yellow", "sky_blue", "green"]:
                if opponent_color != color and opponent_color != teammate_color:
                    if self._position_occupied_by_color(new_pos, opponent_color):
                        # Can capture opponent (this is actually good)
                        return True
            
            return True
            
        except Exception as e:
            print(f"Move validation error: {e}")
            return True  # Default to allowing move

    def _position_occupied_by_color(self, position: int, color: str) -> bool:
        """Check if a position is occupied by a specific color."""
        try:
            color_positions = self._get_positions_and_dice(color)[0]
            return position in color_positions and position != -1
        except Exception:
            return False

    def _enhanced_ai_strategy(self, color: str, legal_moves: List[int]) -> int:
        """Enhanced AI decision making with multiple strategies."""
        if not legal_moves:
            return legal_moves[0] if legal_moves else 1
        
        positions, dice = self._get_positions_and_dice(color)
        
        if self.ai_strategy == AIStrategy.RANDOM:
            return random.choice(legal_moves)
        
        elif self.ai_strategy == AIStrategy.AGGRESSIVE:
            return self._aggressive_ai_move(color, legal_moves, positions, dice)
        
        elif self.ai_strategy == AIStrategy.DEFENSIVE:
            return self._defensive_ai_move(color, legal_moves, positions, dice)
        
        else:  # SMART strategy
            return self._smart_ai_move(color, legal_moves, positions, dice)

    def _aggressive_ai_move(self, color: str, legal_moves: List[int], 
                           positions: List[int], dice: int) -> int:
        """Aggressive AI prioritizes captures and advancement."""
        best_move = legal_moves[0]
        best_score = -1
        
        for move in legal_moves:
            score = 0
            pos = positions[move - 1]
            new_pos = pos + dice if pos != -1 else 1
            
            # High priority for captures
            if self._would_capture_opponent(new_pos, color):
                score += 50
            
            # Priority for getting tokens out
            if pos == -1 and dice == 6:
                score += 30
            
            # Priority for reaching finish
            if new_pos >= 100:
                score += 25
            
            # Priority for advancement
            score += new_pos - (pos if pos != -1 else 0)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move

    def _defensive_ai_move(self, color: str, legal_moves: List[int], 
                          positions: List[int], dice: int) -> int:
        """Defensive AI prioritizes safety and team support."""
        best_move = legal_moves[0]
        best_score = -1
        
        teammate_color = self.get_teammate_color(color)
        
        for move in legal_moves:
            score = 0
            pos = positions[move - 1]
            new_pos = pos + dice if pos != -1 else 1
            
            # Priority for reaching finish safely
            if new_pos >= 100:
                score += 40
            
            # Priority for supporting teammate
            if self._would_support_teammate(new_pos, teammate_color):
                score += 30
            
            # Avoid risky positions
            if self._is_safe_position(new_pos, color):
                score += 20
            
            # Getting tokens out is good
            if pos == -1 and dice == 6:
                score += 25
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move

    def _smart_ai_move(self, color: str, legal_moves: List[int], 
                      positions: List[int], dice: int) -> int:
        """Smart AI balances all factors with situational awareness."""
        best_move = legal_moves[0]
        best_score = -1
        
        teammate_color = self.get_teammate_color(color)
        game_phase = self._determine_game_phase()
        
        for move in legal_moves:
            score = 0
            pos = positions[move - 1]
            new_pos = pos + dice if pos != -1 else 1
            
            # Dynamic scoring based on game phase
            if game_phase == "early":
                score += self._early_game_score(pos, new_pos, dice, color)
            elif game_phase == "mid":
                score += self._mid_game_score(pos, new_pos, dice, color, teammate_color)
            else:  # late game
                score += self._late_game_score(pos, new_pos, dice, color)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move

    def _determine_game_phase(self) -> str:
        """Determine current game phase based on token positions."""
        total_advanced = 0
        total_tokens = 0
        
        for color in ["red", "yellow", "sky_blue", "green"]:
            positions, _ = self._get_positions_and_dice(color)
            for pos in positions:
                total_tokens += 1
                if pos > 30:  # Advanced tokens
                    total_advanced += 1
        
        if total_advanced / total_tokens < 0.3:
            return "early"
        elif total_advanced / total_tokens < 0.7:
            return "mid"
        else:
            return "late"

    def _early_game_score(self, pos: int, new_pos: int, dice: int, color: str) -> int:
        """Scoring for early game phase with smarter priorities."""
        score = 0
        # Get out from base
        if pos == -1 and dice == 6:
            score += 45
        # Advancement is good early
        if pos != -1 and new_pos > pos:
            score += min(20, (new_pos - pos) * 2)
        # Captures are very good
        if self._would_capture_opponent(new_pos, color):
            score += 35
        # Prefer landing on safe spots
        if self._is_safe_position(new_pos, color):
            score += 10
        # Avoid threatened squares
        if self._is_position_threatened(new_pos, color):
            score -= 20
        return score

    def _mid_game_score(self, pos: int, new_pos: int, dice: int, color: str, teammate_color: str) -> int:
        """Scoring for mid game phase with capture/safety/support balance."""
        score = 0
        # Capture priority
        if self._would_capture_opponent(new_pos, color):
            score += 45
        # Support teammate (stack or proximity) is valuable
        if self._would_support_teammate(new_pos, teammate_color):
            score += 20
        # Advancement
        if pos != -1 and new_pos > pos:
            score += min(24, (new_pos - pos) * 2)
        # Prefer safe squares mid as well
        if self._is_safe_position(new_pos, color):
            score += 8
        # Avoid threatened squares
        if self._is_position_threatened(new_pos, color):
            score -= 25
        return score

    def _late_game_score(self, pos: int, new_pos: int, dice: int, color: str) -> int:
        """Scoring for late game phase with finish priority and risk control."""
        score = 0
        # Prioritize entering/advancing in home stretch
        if new_pos >= 100:
            score += 60
            if new_pos == 106:
                score += 120
        else:
            # Outside home stretch: still value captures
            if self._would_capture_opponent(new_pos, color):
                score += 35
            # Advancement but be conservative
            if pos != -1 and new_pos > pos:
                score += min(18, (new_pos - pos))
            # Prefer safe
            if self._is_safe_position(new_pos, color):
                score += 6
            if self._is_position_threatened(new_pos, color):
                score -= 30
        return score

    def _is_position_threatened(self, position: int, color: str) -> bool:
        """Estimate if opponents could capture this position on their next roll."""
        try:
            if position >= 100 or self._is_safe_position(position, color):
                return False
            # Opponent colors
            opps = [c for c in ["red", "yellow", "sky_blue", "green"] if c != color]
            threat = False
            for opp in opps:
                positions, _ = self._get_positions_and_dice(opp)
                for o in positions:
                    if o < 0 or o >= 100:
                        continue
                    for step in range(1, 7):
                        cand = o + step
                        if cand > 52:
                            cand = ((cand - 1) % 52) + 1
                        if cand == position:
                            threat = True
                            break
                    if threat:
                        break
                if threat:
                    break
            return threat
        except Exception:
            return False

    def _would_capture_opponent(self, position: int, color: str) -> bool:
        """Check if moving to position would capture an opponent."""
        try:
            team = self.get_team_for_color(color)
            opponent_colors = self.team_beta if team == Team.ALPHA else self.team_alpha
            
            for opp_color in opponent_colors:
                if self._position_occupied_by_color(position, opp_color):
                    return True
            return False
        except Exception:
            return False

    def _would_support_teammate(self, position: int, teammate_color: Optional[str]) -> bool:
        """Check if moving to position would support teammate."""
        if not teammate_color:
            return False
        try:
            return self._position_occupied_by_color(position, teammate_color)
        except Exception:
            return False

    def _is_safe_position(self, position: int, color: str) -> bool:
        """Check if position is relatively safe from captures."""
        # Safe positions are typically: starting positions, home stretch, finish area
        if position >= 100 or position in [1, 14, 27, 40]:  # Safe squares
            return True
        return False

    def _auto_turn_for_ai(self, color: str):
        """Enhanced AI turn with better decision making and timing."""
        try:
            # Add slight delay for more natural feel
            self.window.after(800, lambda: self._execute_ai_turn(color))
        except Exception as e:
            print(f"AI turn scheduling error ({color}): {e}")

    def _execute_ai_turn(self, color: str):
        """Execute the AI turn with enhanced logic."""
        try:
            # Show AI thinking message
            self._show_ai_thinking(color)
            
            # Roll dice
            self.make_prediction(color)
            
            # Get legal moves
            legal = self._legal_moves_for(color)
            if not legal:
                return  # No moves available
            
            # Use enhanced AI strategy
            chosen_move = self._enhanced_ai_strategy(color, legal)
            
            # Show AI decision
            self._show_ai_decision(color, chosen_move, legal)
            
            # Execute move after brief delay
            # Base game expects coin index as string (e.g., '1'), not int
            self.window.after(500, lambda: self.main_controller(color, str(chosen_move)))
            
        except Exception as e:
            print(f"AI turn execution error ({color}): {e}")

    def _show_ai_thinking(self, color: str):
        """Show AI thinking animation/message."""
        try:
            if self._ui_elements.get("turn_text_id"):
                thinking_text = f"🤖 {color.upper()} AI is thinking..."
                self.make_canvas.itemconfig(
                    self._ui_elements["turn_text_id"], 
                    text=thinking_text, 
                    fill="#f59e0b"
                )
        except Exception:
            pass

    def _show_ai_decision(self, color: str, chosen_move: int, legal_moves: List[int]):
        """Show what the AI decided to do."""
        try:
            decision_text = f"🤖 {color.upper()} AI chose coin {chosen_move}"
            if len(legal_moves) > 1:
                decision_text += f" (from options: {legal_moves})"
                
            print(f"AI Decision: {decision_text}")  # For debugging
        except Exception as e:
            print(f"AI decision display error: {e}")

    # ... (continuing with enhanced UI methods and other improvements)

    def _apply_enhanced_team_theme(self):
        """Apply enhanced team theme with better visual hierarchy."""
        try:
            # Enhanced window setup
            self.window.title("🏆 Team-Up Ludo Championship Arena")
            self.window.configure(bg="#0a0a0a")
            
            # Larger canvas for better team UI
            self.make_canvas.config(bg="#0d1421", width=1000, height=750)
            
            # Enhanced background with better gradients
            self._create_enhanced_background()
            
            # Create main UI elements
            self._create_glowing_banner()
            self._style_team_quadrants()
            self._create_team_battle_ui()
            self._add_decorative_elements()
            
        except Exception as e:
            print(f"Theme application error: {e}")

    def make_command(self, robo_operator=None):
        """Override with enhanced team features and AI handling."""
        # Ensure strict turn order for vs-computer before advancing
        self._enforce_vs_computer_turn_order()
        super().make_command(robo_operator)
        
        # Update team UI only when enhanced UI is active
        if not getattr(self, 'use_classic_ui', False):
            self._update_team_turn_banner()
            self._update_game_statistics()
        
        # Handle AI turns
        if self.is_teamup_vs_computer:
            try:
                color = self._current_turn_color()
                if color in self.ai_team_colors:
                    self._auto_turn_for_ai(color)
            except Exception as e:
                print(f"AI turn handling error: {e}")

    def _update_game_statistics(self):
        """Update and display game statistics."""
        try:
            self.game_stats["moves_played"] += 1
            
            # Update UI if statistics panel exists
            if hasattr(self, '_stats_panel_id'):
                stats_text = f"Moves: {self.game_stats['moves_played']} | "
                stats_text += f"Captures: {self.game_stats['captures_made']} | "
                stats_text += f"Sixes: {self.game_stats['sixes_rolled']}"
                
                self.make_canvas.itemconfig(self._stats_panel_id, text=stats_text)
                
        except Exception as e:
            print(f"Statistics update error: {e}")

    def check_winner_and_runner(self, color_coin: str) -> bool:
        """Enhanced winner checking with better team victory logic."""
        # Check individual player completion
        if not self._check_individual_completion(color_coin):
            return True  # Game continues
        
        # Player completed - add to finished set
        self.finished_colors.add(color_coin)
        self._show_player_completion(color_coin)
        
        # Remove completed player from turn order
        self._remove_player_from_turns(color_coin)
        
        # Check for team victory
        team_victory_result = self._check_team_victory()
        if team_victory_result:
            return False  # Game ends
        
        return True  # Game continues

    def _check_individual_completion(self, color_coin: str) -> bool:
        """Check if an individual player has completed."""
        try:
            position_mappings = {
                "red": (self.red_coord_store, 0),
                "green": (self.green_coord_store, 3),
                "yellow": (self.yellow_coord_store, 2),
                "sky_blue": (self.sky_blue_coord_store, 1)
            }
            
            if color_coin not in position_mappings:
                return False
                
            coord_store, _ = position_mappings[color_coin]
            
            # Check if all tokens are at position 106 (finish)
            return all(pos == 106 for pos in coord_store)
            
        except Exception as e:
            print(f"Individual completion check error: {e}")
            return False

    def _remove_player_from_turns(self, color_coin: str):
        """Remove completed player from turn rotation."""
        try:
            color_to_index = {
                "red": 0, "sky_blue": 1, "yellow": 2, "green": 3
            }
            
            player_index = color_to_index.get(color_coin)
            if player_index is not None and player_index in self.total_people_play:
                self.total_people_play.remove(player_index)
                if self.time_for >= len(self.total_people_play):
                    self.time_for = 0
                elif self.time_for > 0:
                    self.time_for -= 1
                    
            # Disable the player's predict button
            if player_index < len(self.block_value_predict):
                self.block_value_predict[player_index][1]['state'] = 'disabled'
                
        except Exception as e:
            print(f"Player removal error: {e}")

    def _check_team_victory(self) -> bool:
        """Enhanced team victory checking with detailed results."""
        try:
            alpha_completed = self.team_alpha.issubset(self.finished_colors)
            beta_completed = self.team_beta.issubset(self.finished_colors)
            
            if alpha_completed and not beta_completed:
                self._celebrate_team_victory(Team.ALPHA)
                return True
            elif beta_completed and not alpha_completed:
                self._celebrate_team_victory(Team.BETA)
                return True
            elif alpha_completed and beta_completed:
                self._handle_draw_situation()
                return True
                
            return False
            
        except Exception as e:
            print(f"Team victory check error: {e}")
            return False

    def _handle_draw_situation(self):
        """Handle the rare case of simultaneous team completion."""
        draw_message = "🤝 INCREDIBLE DRAW! 🤝\n\n"
        draw_message += "Both teams completed simultaneously!\n"
        draw_message += "This is an extremely rare occurrence!\n\n"
        draw_message += f"Final Stats:\n"
        draw_message += f"• Total Moves: {self.game_stats['moves_played']}\n"
        draw_message += f"• Captures Made: {self.game_stats['captures_made']}\n"
        draw_message += f"• Sixes Rolled: {self.game_stats['sixes_rolled']}"
        
        messagebox.showinfo("🏆 EPIC DRAW! 🏆", draw_message)
        self._end_game(winner_team=None)

    def _celebrate_team_victory(self, winning_team: Team):
        """Enhanced team victory celebration with animations and statistics."""
        try:
            team_name = self.team_names.get(winning_team.value, f"Team {winning_team.value.title()}")
            team_colors = self.team_colors.get(winning_team)
            
            # Create victory message with detailed statistics
            victory_message = f"🎉 {team_name.upper()} WINS! 🎉\n\n"
            victory_message += "🏆 CHAMPIONSHIP VICTORY! 🏆\n\n"
            victory_message += f"Game Statistics:\n"
            victory_message += f"• Total Moves Played: {self.game_stats['moves_played']}\n"
            victory_message += f"• Captures Made: {self.game_stats['captures_made']}\n"
            victory_message += f"• Lucky Sixes: {self.game_stats['sixes_rolled']}\n\n"
            
            if self.is_teamup_vs_computer:
                if winning_team == Team.ALPHA:
                    victory_message += "🎯 Humans triumph over AI!\n"
                else:
                    victory_message += f"🤖 AI ({self.ai_strategy.value.title()}) wins!\n"
            
            victory_message += "Congratulations to the winning team! 🎊"
            
            # Show victory dialog
            messagebox.showinfo("🏆 TEAM VICTORY! 🏆", victory_message)
            
            # Update UI with victory state
            self._update_victory_ui(winning_team, team_colors)
            
            # End game
            self._end_game(winner_team=winning_team.value)
            
        except Exception as e:
            print(f"Victory celebration error: {e}")

    def _update_victory_ui(self, winning_team: Team, team_colors: Optional[Dict]):
        """Update UI to show victory state."""
        try:
            team_name = self.team_names.get(winning_team.value, f"Team {winning_team.value.title()}")
            color = team_colors.get("primary", "#fbbf24") if team_colors else "#fbbf24"
            
            # Update main turn banner
            if self._ui_elements.get("turn_text_id"):
                victory_text = f"🏆 {team_name.upper()} CHAMPIONS! 🏆"
                self.make_canvas.itemconfig(
                    self._ui_elements["turn_text_id"], 
                    text=victory_text,
                    fill=color,
                    font=("Arial Black", 16, "bold")
                )
            
            # Update turn background with victory colors
            if self._ui_elements.get("turn_bg_id"):
                self.make_canvas.itemconfig(
                    self._ui_elements["turn_bg_id"], 
                    outline=color,
                    width=3
                )
                
        except Exception as e:
            print(f"Victory UI update error: {e}")

    def _end_game(self, winner_team: Optional[str]):
        """Enhanced game ending with better statistics and options."""
        try:
            # Disable all predict buttons
            self._disable_all_predict_buttons()
            
            # Update win counters
            if winner_team == "alpha":
                self.alpha_wins += 1
            elif winner_team == "beta":
                self.beta_wins += 1
            
            # Update score display
            self._update_score_display()
            
            # Show game over options
            self._show_game_over_options()
            
        except Exception as e:
            print(f"Game ending error: {e}")

    def _update_score_display(self):
        """Update the score display with current win counts."""
        try:
            if self._ui_elements.get("alpha_score_id"):
                alpha_text = f"🏆 {self.team_names['alpha'].upper()}: {self.alpha_wins}"
                self.make_canvas.itemconfig(
                    self._ui_elements["alpha_score_id"], 
                    text=alpha_text
                )
            
            if self._ui_elements.get("beta_score_id"):
                beta_text = f"🏆 {self.team_names['beta'].upper()}: {self.beta_wins}"
                self.make_canvas.itemconfig(
                    self._ui_elements["beta_score_id"], 
                    text=beta_text
                )
                
        except Exception as e:
            print(f"Score display update error: {e}")

    def _show_game_over_options(self):
        """Show options for what to do after game ends."""
        try:
            options_window = tk.Toplevel(self.window)
            options_window.title("🎮 Game Complete")
            options_window.geometry("400x300")
            options_window.config(bg="#0a0a0a")
            options_window.resizable(False, False)
            
            # Center the window
            options_window.transient(self.window)
            options_window.grab_set()
            
            # Title
            title_label = tk.Label(
                options_window, 
                text="🎮 Game Complete! 🎮",
                font=("Arial Black", 18, "bold"),
                bg="#0a0a0a", 
                fg="#fbbf24"
            )
            title_label.pack(pady=20)
            
            # Current score display
            score_text = f"Series Score:\n{self.team_names['alpha']}: {self.alpha_wins} wins\n{self.team_names['beta']}: {self.beta_wins} wins"
            score_label = tk.Label(
                options_window,
                text=score_text,
                font=("Arial", 12, "bold"),
                bg="#0a0a0a",
                fg="#cbd5e1",
                justify=tk.CENTER
            )
            score_label.pack(pady=10)
            
            # Buttons frame
            button_frame = tk.Frame(options_window, bg="#0a0a0a")
            button_frame.pack(pady=20)
            
            # Play again button
            play_again_btn = tk.Button(
                button_frame,
                text="🔄 Play Again",
                font=("Arial", 12, "bold"),
                bg="#10b981",
                fg="white",
                width=12,
                height=2,
                command=lambda: [options_window.destroy(), self._start_new_game()]
            )
            play_again_btn.pack(side=tk.LEFT, padx=10)
            
            # New teams button
            new_teams_btn = tk.Button(
                button_frame,
                text="👥 New Teams",
                font=("Arial", 12, "bold"),
                bg="#3b82f6",
                fg="white",
                width=12,
                height=2,
                command=lambda: [options_window.destroy(), self._setup_new_teams()]
            )
            new_teams_btn.pack(side=tk.LEFT, padx=10)
            
            # Quit button
            quit_btn = tk.Button(
                button_frame,
                text="🚪 Quit",
                font=("Arial", 12, "bold"),
                bg="#ef4444",
                fg="white",
                width=12,
                height=2,
                command=lambda: [options_window.destroy(), self.window.quit()]
            )
            quit_btn.pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            print(f"Game over options error: {e}")

    def _start_new_game(self):
        """Start a new game with same teams and settings."""
        try:
            # Reset game state but keep team settings
            self.finished_colors.clear()
            self.game_stats = {k: 0 for k in self.game_stats}
            
            # Reset UI
            self._update_team_turn_banner()
            
            # Start new game
            self.time_for = -1
            self.make_command()
            
            # Show new game message
            messagebox.showinfo("🎮 New Game", "New game started with same teams!\nLet the battle continue!")
            
        except Exception as e:
            print(f"New game start error: {e}")

    def _setup_new_teams(self):
        """Setup completely new teams and settings."""
        try:
            # Reset everything
            self.finished_colors.clear()
            self.game_stats = {k: 0 for k in self.game_stats}
            self.alpha_wins = 0
            self.beta_wins = 0
            
            # Start fresh setup
            self.take_initial_control()
            
        except Exception as e:
            print(f"New teams setup error: {e}")

    def coord_overlap(self, counter_coin, color_coin, path_to_traverse_before_overlap):
        """Enhanced overlap handling with better teammate mechanics."""
        try:
            # Determine team relationships
            current_team = self.get_team_for_color(color_coin)
            
            # Check what's at the target position
            position_info = self._analyze_position_occupancy(counter_coin)
            
            if position_info["teammate_present"]:
                self._handle_teammate_stacking(counter_coin, color_coin, position_info)
                return
            elif position_info["opponent_present"]:
                self._handle_opponent_capture(counter_coin, color_coin, position_info)
                # Update capture statistics
                self.game_stats["captures_made"] += 1
                return
            
            # No overlap - normal move
            super().coord_overlap(counter_coin, color_coin, path_to_traverse_before_overlap)
            
        except Exception as e:
            print(f"Enhanced overlap handling error: {e}")
            # Fallback to original method
            super().coord_overlap(counter_coin, color_coin, path_to_traverse_before_overlap)

    def _analyze_position_occupancy(self, position: int) -> Dict:
        """Analyze what pieces are at a given position."""
        occupancy_info = {
            "teammate_present": False,
            "opponent_present": False,
            "occupying_colors": [],
            "position": position
        }
        
        try:
            # Check all colors for pieces at this position
            for color in ["red", "yellow", "sky_blue", "green"]:
                positions, _ = self._get_positions_and_dice(color)
                if position in positions and position != -1:
                    occupancy_info["occupying_colors"].append(color)
            
            return occupancy_info
            
        except Exception as e:
            print(f"Position analysis error: {e}")
            return occupancy_info

    def _handle_teammate_stacking(self, position: int, moving_color: str, position_info: Dict):
        """Handle when a piece moves to a teammate's position."""
        try:
            teammate_colors = [c for c in position_info["occupying_colors"] 
                             if self.get_team_for_color(c) == self.get_team_for_color(moving_color)]
            
            if teammate_colors:
                # Show enhanced teammate protection message
                team_name = self.team_names.get(
                    self.get_team_for_color(moving_color).value, 
                    "Team"
                )
                
                message = f"🤝 {team_name} Teamwork! 🤝\n\n"
                message += f"{moving_color.replace('_', ' ').title()} safely joins "
                message += f"{', '.join([c.replace('_', ' ').title() for c in teammate_colors])}\n\n"
                message += "Teammates protect each other on the battlefield! 🛡️"
                
                messagebox.showinfo("🤝 Teammate Support", message)
                
        except Exception as e:
            print(f"Teammate stacking error: {e}")

    def _handle_opponent_capture(self, position: int, capturing_color: str, position_info: Dict):
        """Handle when a piece captures an opponent."""
        try:
            capturing_team = self.get_team_for_color(capturing_color)
            opponent_colors = [c for c in position_info["occupying_colors"] 
                             if self.get_team_for_color(c) != capturing_team]
            
            if opponent_colors:
                # Show enhanced capture message
                message = f"⚔️ EPIC CAPTURE! ⚔️\n\n"
                message += f"{capturing_color.replace('_', ' ').title()} captures "
                message += f"{', '.join([c.replace('_', ' ').title() for c in opponent_colors])}!\n\n"
                message += f"Opponent tokens return to base! 🏠"
                
                messagebox.showinfo("⚔️ Capture!", message)
                
                # Apply capture logic (send opponents home)
                self._send_tokens_home(opponent_colors, position)
                
        except Exception as e:
            print(f"Opponent capture error: {e}")

    def _send_tokens_home(self, colors_to_send_home: List[str], position: int):
        """Send captured tokens back to their starting positions."""
        try:
            position_mappings = {
                "red": self.red_coord_store,
                "yellow": self.yellow_coord_store,
                "sky_blue": self.sky_blue_coord_store,
                "green": self.green_coord_store
            }
            
            for color in colors_to_send_home:
                if color in position_mappings:
                    coord_store = position_mappings[color]
                    # Find tokens at the capture position and send them home
                    for i, pos in enumerate(coord_store):
                        if pos == position:
                            coord_store[i] = -1  # Send back to start
                            
        except Exception as e:
            print(f"Send tokens home error: {e}")

    def make_prediction(self, color_coin):
        """Override to track six rolls and add enhanced feedback."""
        try:
            # Call parent prediction method
            result = super().make_prediction(color_coin)
            # Play dice sound after result
            try:
                self.play_dice_sound()
            except Exception:
                pass
            
            # Check if a six was rolled (this would need to be determined from the dice result)
            # For now, we'll assume we can check the current dice value
            current_dice = self._get_current_dice_value(color_coin)
            if current_dice == 6:
                self.game_stats["sixes_rolled"] += 1
                self._show_six_celebration(color_coin)
            
            return result
            
        except Exception as e:
            print(f"Enhanced prediction error: {e}")
            return super().make_prediction(color_coin)

    def _get_current_dice_value(self, color_coin: str) -> int:
        """Get the current dice value for a color."""
        try:
            dice_mapping = {
                "red": self.move_red_counter,
                "yellow": self.move_yellow_counter, 
                "sky_blue": self.move_sky_blue_counter,
                "green": self.move_green_counter
            }
            return dice_mapping.get(color_coin, 1)
        except Exception:
            return 1

    def _show_six_celebration(self, color_coin: str):
        """Show celebration for rolling a six."""
        try:
            # Brief visual feedback for rolling a six
            team = self.get_team_for_color(color_coin)
            team_name = self.team_names.get(team.value, "Team")
            
            # This could be expanded to include visual animations
            print(f"🎲 {color_coin.title()} rolled a SIX! Extra turn for {team_name}! 🎲")
            
        except Exception as e:
            print(f"Six celebration error: {e}")

    def _ask_player_names(self, num_players: int = 4, vs_computer: bool = False):
        """Team-Up prompt: ask only human names and team names.
        - vs_computer=True: Red + Yellow are humans; Sky Blue + Green are fixed bots (bot1/bot2).
        - vs_computer=False: prompt all four human players.
        """
        try:
            name_win = tk.Toplevel(self.window)
            name_win.title("Enter Team and Player Names")
            name_win.geometry("420x320")
            name_win.resizable(False, False)

            # Team names
            tk.Label(name_win, text="Team Names:", font=("Arial", 12, "bold")).place(x=20, y=12)
            tk.Label(name_win, text="Team Alpha:").place(x=40, y=40)
            alpha_ent = tk.Entry(name_win, width=28)
            alpha_ent.insert(0, self.team_names.get("alpha", "Team Alpha"))
            alpha_ent.place(x=140, y=40)

            tk.Label(name_win, text="Team Beta:").place(x=40, y=70)
            beta_ent = tk.Entry(name_win, width=28)
            beta_ent.insert(0, self.team_names.get("beta", "Team Beta"))
            beta_ent.place(x=140, y=70)

            tk.Label(name_win, text="Player Names:", font=("Arial", 12, "bold")).place(x=20, y=110)

            # Rows start at y=140
            row = 0
            entries = []  # list of (index, entry)

            def add_editable(idx: int, label_text: str, default_text: str):
                nonlocal row
                tk.Label(name_win, text=label_text, width=12, anchor="w").place(x=40, y=140 + row * 35)
                ent = tk.Entry(name_win, width=28)
                ent.insert(0, default_text)
                ent.place(x=140, y=140 + row * 35)
                entries.append((idx, ent))
                row += 1

            def add_fixed(label_text: str, fixed_text: str):
                nonlocal row
                tk.Label(name_win, text=label_text, width=12, anchor="w").place(x=40, y=140 + row * 35)
                lab = tk.Label(name_win, text=fixed_text, width=28, anchor="w", relief=tk.SUNKEN, bd=1)
                lab.place(x=140, y=140 + row * 35)
                row += 1

            # Defaults from current player_names or fallbacks
            def_name = lambda i: self.player_names.get(i, f"Player {i+1}")

            if vs_computer:
                # Humans: Red(0), Yellow(2). Bots fixed for Sky Blue(1)=bot1, Green(3)=bot2
                self.player_names[1] = "bot1"
                self.player_names[3] = "bot2"
                add_editable(0, "Red", def_name(0))
                add_fixed("Sky Blue", "bot1")
                add_editable(2, "Yellow", def_name(2))
                add_fixed("Green", "bot2")
            else:
                add_editable(0, "Red", def_name(0))
                add_editable(1, "Sky Blue", def_name(1))
                add_editable(2, "Yellow", def_name(2))
                add_editable(3, "Green", def_name(3))

            def apply_and_close():
                # Save team names
                self.team_names["alpha"] = alpha_ent.get().strip() or "Team Alpha"
                self.team_names["beta"] = beta_ent.get().strip() or "Team Beta"
                try:
                    self.set_team_names(self.team_names["alpha"], self.team_names["beta"])
                except Exception:
                    pass

                # Save player names for editable entries only
                for idx, ent in entries:
                    text = ent.get().strip() or f"Player {idx+1}"
                    self.player_names[idx] = text
                try:
                    self._apply_player_names_to_labels()
                except Exception:
                    pass

                name_win.destroy()

            tk.Button(name_win, text="Apply", command=apply_and_close).place(x=175, y=140 + row * 35 + 10)
            name_win.grab_set()
            name_win.focus_set()
        except Exception as e:
            print(f"TeamUp name prompt error: {e}")

    def _create_enhanced_background(self):
        """Create an enhanced background with better visual effects."""
        try:
            # Create a more sophisticated gradient background
            canvas_width = 1000
            canvas_height = 750
            
            # Multiple gradient layers for depth
            gradient_colors = [
                ("#0d1421", "#1a1f3a"),
                ("#1a1f3a", "#0d1421"), 
                ("#0a0a0a", "#1a1f3a")
            ]
            
            for i, (start_color, end_color) in enumerate(gradient_colors):
                # Create gradient effect using multiple rectangles
                layer_height = canvas_height // len(gradient_colors)
                y_start = i * layer_height
                
                for j in range(layer_height):
                    # Simple gradient simulation
                    alpha = j / layer_height
                    # Use alternating pattern for visual interest
                    color = start_color if j % 20 < 10 else end_color
                    
                    self.make_canvas.create_rectangle(
                        0, y_start + j, canvas_width, y_start + j + 1,
                        fill=color, outline=""
                    )
            
        except Exception as e:
            print(f"Enhanced background creation error: {e}")

    def _create_glowing_banner(self):
        """Create an enhanced glowing banner with better effects."""
        try:
            # Enhanced main title banner with multiple layers for glow effect
            banner_layers = [
                {"offset": 4, "color": "#1e3a8a", "width": 3},
                {"offset": 2, "color": "#3b82f6", "width": 2},
                {"offset": 0, "color": "#60a5fa", "width": 1}
            ]
            
            for layer in banner_layers:
                self.make_canvas.create_rectangle(
                    10 - layer["offset"], 10 - layer["offset"], 
                    990 + layer["offset"], 70 + layer["offset"],
                    fill="", outline=layer["color"], width=layer["width"]
                )
            
            # Enhanced background fill
            self.make_canvas.create_rectangle(
                10, 10, 990, 70,
                fill="#1e3a8a", outline="", stipple="gray25"
            )
            
            # Title with shadow effect
            shadow_offset = 2
            self.make_canvas.create_text(
                502 + shadow_offset, 42 + shadow_offset, 
                text="⚔️ TEAM BATTLE CHAMPIONSHIP ARENA ⚔️", 
                font=("Arial Black", 20, "bold"), 
                fill="#000000"  # Shadow
            )
            
            self.make_canvas.create_text(
                500, 40, 
                text="⚔️ TEAM BATTLE CHAMPIONSHIP ARENA ⚔️", 
                font=("Arial Black", 20, "bold"), 
                fill="#fbbf24"  # Main text
            )
            
            # Enhanced subtitle with team names
            self._ui_elements["subtitle_id"] = self.make_canvas.create_text(
                500, 55, 
                text=f"{self.team_names['alpha']} vs {self.team_names['beta']}",
                font=("Arial", 12, "bold"), 
                fill="#cbd5e1"
            )
            
        except Exception as e:
            print(f"Enhanced banner creation error: {e}")

    def set_team_names(self, alpha_team_name: str, beta_team_name: str):
        """Enhanced team name setting with better UI updates."""
        try:
            # Store the names
            self.team_names["alpha"] = alpha_team_name or "Team Alpha"
            self.team_names["beta"] = beta_team_name or "Team Beta"

            # Update all UI elements that reference team names
            ui_updates = [
                ("alpha_name_id", self.team_names["alpha"].upper()),
                ("beta_name_id", self.team_names["beta"].upper()),
                ("subtitle_id", f"{self.team_names['alpha']} vs {self.team_names['beta']}")
            ]
            
            for element_key, text in ui_updates:
                element_id = self._ui_elements.get(element_key)
                if element_id:
                    self.make_canvas.itemconfig(element_id, text=text)
            
            # Update scoreboard
            self._update_score_display()
            
            # Update turn banner if needed
            self._update_team_turn_banner()
            
        except Exception as e:
            print(f"Enhanced team name setting error: {e}")

    def _current_turn_color(self) -> str:
        """Get current turn color with better error handling."""
        try:
            if not self.total_people_play or self.time_for < 0:
                return 'red'  # Default fallback
                
            if self.time_for >= len(self.total_people_play):
                return 'red'  # Default fallback
                
            idx = self.total_people_play[self.time_for]
            color_map = {0: 'red', 1: 'sky_blue', 2: 'yellow', 3: 'green'}
            return color_map.get(idx, 'red')
            
        except Exception as e:
            print(f"Current turn color error: {e}")
            return 'red'

    def _update_team_turn_banner(self):
        """Enhanced turn banner with better animations and styling."""
        try:
            if not self.total_people_play:
                return
                
            current_color = self._current_turn_color()
            current_team = self.get_team_for_color(current_color)
            
            # Enhanced player display names
            player_display_names = {
                "red": "🔴 RED WARRIOR",
                "green": "🟢 GREEN GUARDIAN", 
                "yellow": "🟡 YELLOW CHAMPION",
                "sky_blue": "🔵 BLUE STRIKER"
            }
            
            # Team information
            team_info = {
                Team.ALPHA: {
                    "name": f"{self.team_names['alpha'].upper()} COALITION",
                    "color": "#dc2626",
                    "bg_color": "#fee2e2"
                },
                Team.BETA: {
                    "name": f"{self.team_names['beta'].upper()} ALLIANCE",
                    "color": "#0ea5e9", 
                    "bg_color": "#e0f2fe"
                }
            }
            
            team_data = team_info[current_team]
            player_name = player_display_names.get(current_color, current_color.upper())
            
            # Enhanced turn text
            turn_text = f"{team_data['name']} • {player_name}"
            if self.is_teamup_vs_computer and current_color in self.ai_team_colors:
                turn_text += f" (AI-{self.ai_strategy.value.title()})"
            
            # Update UI elements
            if self._ui_elements.get("turn_text_id"):
                self.make_canvas.itemconfig(
                    self._ui_elements["turn_text_id"], 
                    text=turn_text, 
                    fill=team_data["color"]
                )
            
            if self._ui_elements.get("turn_bg_id"):
                self.make_canvas.itemconfig(
                    self._ui_elements["turn_bg_id"], 
                    outline=team_data["color"],
                    width=2
                )
                
            # Update team status indicators
            self._update_team_status_indicators(current_color)
            
        except Exception as e:
            print(f"Enhanced turn banner update error: {e}")

    def _create_team_status_panels(self):
        """Create enhanced team status and information panels."""
        try:
            # Main scoreboard background with enhanced styling
            scoreboard_bg = self.make_canvas.create_rectangle(
                200, 680, 800, 730, 
                fill="#1f2937", outline="#6b7280", width=2,
                stipple="gray12"
            )
            
            # Team scores with enhanced styling and icons
            self._ui_elements["alpha_score_id"] = self.make_canvas.create_text(
                300, 705, 
                text=f"🏆 {self.team_names['alpha'].upper()}: {self.alpha_wins}", 
                font=("Arial Black", 14, "bold"), 
                fill="#dc2626"
            )
            
            self._ui_elements["beta_score_id"] = self.make_canvas.create_text(
                700, 705, 
                text=f"🏆 {self.team_names['beta'].upper()}: {self.beta_wins}", 
                font=("Arial Black", 14, "bold"), 
                fill="#0ea5e9"
            )
            
            # Enhanced turn indicator with glowing background
            self._ui_elements["turn_bg_id"] = self.make_canvas.create_rectangle(
                250, 80, 750, 110, 
                fill="#1f2937", outline="#fbbf24", width=2,
                stipple="gray25"
            )
            
            self._ui_elements["turn_text_id"] = self.make_canvas.create_text(
                500, 95, 
                text="PREPARING BATTLE...", 
                font=("Arial Black", 16, "bold"), 
                fill="#ffffff"
            )
            
            # Game statistics panel
            self._create_statistics_panel()
            
        except Exception as e:
            print(f"Enhanced status panels creation error: {e}")

    def _create_statistics_panel(self):
        """Create a statistics panel to show game progress."""
        try:
            # Statistics background
            stats_bg = self.make_canvas.create_rectangle(
                50, 680, 180, 730,
                fill="#374151", outline="#6b7280", width=1
            )
            
            # Statistics text
            self._stats_panel_id = self.make_canvas.create_text(
                115, 705,
                text="Game Stats",
                font=("Arial", 10, "bold"),
                fill="#cbd5e1"
            )
            
        except Exception as e:
            print(f"Statistics panel creation error: {e}")