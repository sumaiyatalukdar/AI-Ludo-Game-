from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import time
from random import randint

from Ludo_game_with_Sam import Ludo


class LudoRush(Ludo):
	def __init__(self, root, six_side_block, five_side_block, four_side_block, three_side_block, two_side_block, one_side_block):
		self.is_rush_mode = True
		self.turn_time_limit_sec = 5
		self._rush_after_id = None
		self._rush_phase = None
		self.rush_bots = set()  # colors that are bots
		super().__init__(root, six_side_block, five_side_block, four_side_block, three_side_block, two_side_block, one_side_block)

	# --------- Rush startup (override) ---------
	def take_initial_control(self):
		for i in range(4):
			self.block_value_predict[i][1]['state'] = DISABLED

		top = Toplevel()
		top.geometry("530x260")
		top.maxsize(530,260)
		top.minsize(530,260)
		top.config(bg="#141414")
		top.iconbitmap("Images/ludo_icon.ico")

		head = Label(top, text="Rush Mode", font=("Arial", 25, "bold", "italic"), bg="#141414", fg="chocolate")
		head.place(x=170, y=22)

		info = Label(top, text="Choose how to play", font=("Arial", 12, "bold"), bg="#141414", fg="#c9c9c9")
		info.place(x=190, y=70)

		def start_rush(vs_computer: bool):
			self.total_people_play.clear()
			if vs_computer:
				# One human on Sky Blue, three bots on Red/Yellow/Green
				self.total_people_play.extend([0,1,2,3])
				self.rush_bots = {"red", "yellow", "green"}
				self.robo_prem = 0
				try:
					self.player_names[0] = "Bot (Red)"
					self.player_names[2] = "Bot (Yellow)"
					self.player_names[3] = "Bot (Green)"
					self.player_names[1] = "You (Sky Blue)"
					self._apply_player_names_to_labels()
				except Exception:
					pass
			else:
				# All humans local on same device
				self.total_people_play.extend([0,1,2,3])
				self.rush_bots = set()
			top.destroy()
			self.make_command()

		mvc_rush_btn = Button(top, text="Rush: Vs Computer", bg="#262626", fg="#00FF00", font=("Arial", 15, "bold"), relief=RAISED, bd=3, command=lambda: start_rush(True), activebackground="#262626")
		mvc_rush_btn.place(x=40, y=120)

		mvh_rush_btn = Button(top, text="Rush: With Friends", bg="#262626", fg="#00FF00", font=("Arial", 15, "bold"), relief=RAISED, bd=3, command=lambda: start_rush(False), activebackground="#262626")
		mvh_rush_btn.place(x=280, y=120)

		top.mainloop()

	# --------- Rush turn flow (override) ---------
	def make_command(self, robo_operator=None):
		self._cancel_rush_timer()
		if self.time_for != -1:
			self.block_value_predict[self.total_people_play[self.time_for]][1]['state'] = DISABLED
		if self.time_for == len(self.total_people_play) - 1:
			self.time_for = -1
		self.time_for += 1
		self.block_value_predict[self.total_people_play[self.time_for]][1]['state'] = NORMAL

		color = self._current_turn_color()
		if self._is_bot_turn(color):
			# Bot plays instantly
			self._bot_play(color)
		else:
			# Human: start predict timer
			self._start_rush_timer_predict(color)

	# --------- Rush dice roll (override to add speed+timer) ---------
	def make_prediction(self, color_indicator):
		try:
			if color_indicator == "red":
				block_value_predict = self.block_value_predict[0]
				permanent_block_number = self.move_red_counter = randint(1, 6)
			elif color_indicator == "sky_blue":
				block_value_predict = self.block_value_predict[1]
				permanent_block_number = self.move_sky_blue_counter = randint(1, 6)
			elif color_indicator == "yellow":
				block_value_predict = self.block_value_predict[2]
				permanent_block_number = self.move_yellow_counter = randint(1, 6)
			else:
				block_value_predict = self.block_value_predict[3]
				permanent_block_number = self.move_green_counter = randint(1, 6)

			block_value_predict[1]['state'] = DISABLED
			# Faster dice illusion in Rush
			temp_counter = 8
			while temp_counter > 0:
				move_temp_counter = randint(1, 6)
				block_value_predict[0]['image'] = self.block_number_side[move_temp_counter - 1]
				self.window.update()
				self._sleep(0.06)
				temp_counter -= 1

			block_value_predict[0]['image'] = self.block_number_side[permanent_block_number - 1]
			# Play dice roll sound once when result is finalized
			try:
				self.play_dice_sound()
			except Exception:
				pass
			self.instructional_btn_customization_based_on_current_situation(color_indicator, permanent_block_number, block_value_predict)
			# Start move timer for human
			if not self._is_bot_turn(color_indicator):
				self._start_rush_timer_move(color_indicator)
		except Exception:
			print("Rush: Error in Prediction")

	# --------- Movement speed overrides ---------
	def motion_of_coin(self, counter_coin, specific_coin, number_label, number_label_x, number_label_y, color_coin, path_counter):
		try:
			number_label.place(x=number_label_x, y=number_label_y)
			while True:
				if path_counter == 0:
					break
				elif (counter_coin == 51 and color_coin == "red") or (counter_coin == 12 and color_coin == "green") or (counter_coin == 25 and color_coin == "yellow") or (counter_coin == 38 and color_coin == "sky_blue") or counter_coin >= 100:
					if counter_coin < 100:
						counter_coin = 100
					counter_coin = self.under_room_traversal_control(specific_coin, number_label, number_label_x, number_label_y, path_counter, counter_coin, color_coin)
					if counter_coin == 106:
						messagebox.showinfo("Destination reached", "Congrats! You now at the destination")
						if path_counter == 6:
							self.six_with_overlap = 1
						else:
							self.time_for -= 1
					break
				counter_coin += 1
				path_counter -= 1
				number_label.place_forget()

				if counter_coin <= 5:
					self.make_canvas.move(specific_coin, 40, 0)
					number_label_x += 40
				elif counter_coin == 6:
					self.make_canvas.move(specific_coin, 40, -40)
					number_label_x += 40
					number_label_y -= 40
				elif 6 < counter_coin <= 11:
					self.make_canvas.move(specific_coin, 0, -40)
					number_label_y -= 40
				elif counter_coin <= 13:
					self.make_canvas.move(specific_coin, 40, 0)
					number_label_x += 40
				elif counter_coin <= 18:
					self.make_canvas.move(specific_coin, 0, 40)
					number_label_y += 40
				elif counter_coin == 19:
					self.make_canvas.move(specific_coin, 40, 40)
					number_label_x += 40
					number_label_y += 40
				elif counter_coin <= 24:
					self.make_canvas.move(specific_coin, 40, 0)
					number_label_x += 40
				elif counter_coin <= 26:
					self.make_canvas.move(specific_coin, 0, 40)
					number_label_y += 40
				elif counter_coin <= 31:
					self.make_canvas.move(specific_coin, -40, 0)
					number_label_x -= 40
				elif counter_coin == 32:
					self.make_canvas.move(specific_coin, -40, 40)
					number_label_x -= 40
					number_label_y += 40
				elif counter_coin <= 37:
					self.make_canvas.move(specific_coin, 0, 40)
					number_label_y += 40
				elif counter_coin <= 39:
					self.make_canvas.move(specific_coin, -40, 0)
					number_label_x -= 40
				elif counter_coin <= 44:
					self.make_canvas.move(specific_coin, 0, -40)
					number_label_y -= 40
				elif counter_coin == 45:
					self.make_canvas.move(specific_coin, -40, -40)
					number_label_x -= 40
					number_label_y -= 40
				elif counter_coin <= 50:
					self.make_canvas.move(specific_coin, -40, 0)
					number_label_x -= 40
				elif 50 < counter_coin <= 52:
					self.make_canvas.move(specific_coin, 0, -40)
					number_label_y -= 40
				elif counter_coin == 53:
					self.make_canvas.move(specific_coin, 40, 0)
					number_label_x += 40
					counter_coin = 1

				number_label.place_forget()
				number_label.place(x=number_label_x, y=number_label_y)
				# Play move sound per step
				try:
					self.play_move_sound()
				except Exception:
					pass
				self.window.update()
				self._sleep(0.08)
			return counter_coin
		except Exception:
			print("Rush: Error in motion_of_coin")

	def room_red_traversal(self, specific_coin, number_label, number_label_x, number_label_y, path_counter, counter_coin):
		while path_counter > 0:
			counter_coin += 1
			path_counter -= 1
			self.make_canvas.move(specific_coin, 40, 0)
			number_label_x += 40
			number_label.place(x=number_label_x, y=number_label_y)
			self.window.update()
			try:
				self.play_move_sound()
			except Exception:
				pass
			self._sleep(0.08)
		return counter_coin

	def room_green_traversal(self, specific_coin, number_label, number_label_x, number_label_y, path_counter, counter_coin):
		while path_counter > 0:
			counter_coin += 1
			path_counter -= 1
			self.make_canvas.move(specific_coin, 0, 40)
			number_label_y += 40
			number_label.place(x=number_label_x, y=number_label_y)
			self.window.update()
			try:
				self.play_move_sound()
			except Exception:
				pass
			self._sleep(0.08)
		return counter_coin

	def room_yellow_traversal(self, specific_coin, number_label, number_label_x, number_label_y, path_counter, counter_coin):
		while path_counter > 0:
			counter_coin += 1
			path_counter -= 1
			self.make_canvas.move(specific_coin, -40, 0)
			number_label_x -= 40
			number_label.place(x=number_label_x, y=number_label_y)
			self.window.update()
			try:
				self.play_move_sound()
			except Exception:
				pass
			self._sleep(0.08)
		return counter_coin

	def room_sky_blue_traversal(self, specific_coin, number_label, number_label_x, number_label_y, path_counter, counter_coin):
		while path_counter > 0:
			counter_coin += 1
			path_counter -= 1
			self.make_canvas.move(specific_coin, 0, -40)
			number_label_y -= 40
			number_label.place(x=number_label_x, y=number_label_y)
			self.window.update()
			try:
				self.play_move_sound()
			except Exception:
				pass
			self._sleep(0.08)
		return counter_coin

	# --------- Rush helpers ---------
	def _sleep(self, seconds):
		try:
			time.sleep(min(0.05, seconds))
		except Exception:
			pass

	def _cancel_rush_timer(self):
		try:
			if self._rush_after_id is not None:
				self.window.after_cancel(self._rush_after_id)
		except Exception:
			pass
		self._rush_after_id = None
		self._rush_phase = None

	def _rush_schedule(self, func, delay_ms):
		self._cancel_rush_timer()
		try:
			self._rush_after_id = self.window.after(delay_ms, func)
		except Exception:
			self._rush_after_id = None

	def _current_turn_color(self):
		try:
			idx = self.total_people_play[self.time_for]
			return ["red", "sky_blue", "yellow", "green"][idx]
		except Exception:
			return "red"

	def _is_bot_turn(self, color):
		return color in self.rush_bots

	def _get_positions(self, color):
		return {
			"red": self.red_coin_position,
			"green": self.green_coin_position,
			"yellow": self.yellow_coin_position,
			"sky_blue": self.sky_blue_coin_position,
		}[color]

	def _get_move_counter(self, color):
		return {
			"red": self.move_red_counter,
			"green": self.move_green_counter,
			"yellow": self.move_yellow_counter,
			"sky_blue": self.move_sky_blue_counter,
		}[color]

	def _set_move_counter(self, color, value):
		if color == "red":
			self.move_red_counter = value
		elif color == "green":
			self.move_green_counter = value
		elif color == "yellow":
			self.move_yellow_counter = value
		else:
			self.move_sky_blue_counter = value

	def _safe_squares(self):
		return {1, 9, 14, 22, 27, 35, 40, 48}

	def _legal_moves_generic(self, color):
		dice = self._get_move_counter(color)
		pos_list = self._get_positions(color)
		moves = []
		for coin_idx in range(1, 5):
			pos = pos_list[coin_idx - 1]
			if pos == -1:
				if dice == 6:
					moves.append(coin_idx)
				continue
			if pos >= 100:
				if pos + dice <= 106:
					moves.append(coin_idx)
			else:
				if pos + dice <= 106:
					moves.append(coin_idx)
		return moves

	def _evaluate_move_generic(self, color, coin_index_one_based):
		dice = self._get_move_counter(color)
		pos_list = self._get_positions(color)
		pos = pos_list[coin_index_one_based - 1]
		new_pos = None
		if pos == -1 and dice == 6:
			new_pos = {"red": 1, "green": 14, "yellow": 27, "sky_blue": 40}[color]
		elif pos >= 100:
			if pos + dice <= 106:
				new_pos = pos + dice
			else:
				return float('-inf')
		else:
			if pos + dice <= 106:
				if (color == "red" and pos == 51) or (color == "green" and pos == 12) or (color == "yellow" and pos == 25) or (color == "sky_blue" and pos == 38):
					new_pos = 100 if dice > 0 else pos
				else:
					new_pos = pos + dice
				if new_pos == 53:
					new_pos = 1
			else:
				return float('-inf')

		score = 0.0
		if pos == -1:
			score += 5.0
		else:
			score += max(0, (new_pos - pos)) * 0.5
		if new_pos >= 100:
			score += 8.0
			if new_pos == 106:
				score += 20.0
		if new_pos in self._safe_squares():
			score += 4.0

		# Opponents positions
		all_colors = ["red", "sky_blue", "yellow", "green"]
		opps = []
		for c in all_colors:
			if c == color:
				continue
			opps += [p for p in self._get_positions(c) if p > -1 and p < 106]
		if new_pos < 100 and new_pos in opps and new_pos not in self._safe_squares():
			score += 10.0
		if pos in self._safe_squares() and new_pos not in self._safe_squares():
			score -= 2.0
		if new_pos < 100 and new_pos not in self._safe_squares():
			threat = False
			for o in opps:
				if o >= 100:
					continue
				for step in range(1, 7):
					cand = o + step
					if cand == 53:
						cand = 1
					if cand == new_pos:
						threat = True
						break
				if threat:
					break
			if threat:
				score -= 6.0
		max_current = max([p for p in pos_list if p > -1] + [0])
		if pos == max_current:
			score += 1.0
		return score

	def _choose_best_move(self, color, legal_moves):
		best_score = float('-inf')
		best_move = legal_moves[0]
		for mv in legal_moves:
			s = self._evaluate_move_generic(color, mv)
			if s > best_score:
				best_score = s
				best_move = mv
		return best_move

	def _bot_play(self, color):
		# Auto-roll
		self._set_move_counter(color, randint(1, 6))
		idx = {"red":0, "sky_blue":1, "yellow":2, "green":3}[color]
		val = self._get_move_counter(color)
		self.block_value_predict[idx][0]['image'] = self.block_number_side[val-1]
		# Play dice sound for bot roll too
		try:
			self.play_dice_sound()
		except Exception:
			pass
		self.block_value_predict[idx][1]['state'] = DISABLED
		# Compute legal moves and play best or skip
		legal = self._legal_moves_generic(color)
		if legal:
			chosen = self._choose_best_move(color, legal)
			self.main_controller(color, str(chosen))
		else:
			self.make_command()

	def _start_rush_timer_predict(self, color):
		self._rush_phase = 'predict'
		def on_timeout():
			try:
				idx = {"red":0, "sky_blue":1, "yellow":2, "green":3}[color]
				if self.block_value_predict[idx][1]['state'] == NORMAL:
					self.make_prediction(color)
			except Exception:
				pass
			finally:
				self._rush_after_id = None
		self._rush_schedule(on_timeout, int(self.turn_time_limit_sec * 1000))

	def _start_rush_timer_move(self, color):
		self._rush_phase = 'move'
		def on_timeout():
			try:
				legal = self._legal_moves_generic(color)
				if len(legal) == 1:
					self.main_controller(color, str(legal[0]))
				else:
					self.make_command()
			except Exception:
				try:
					self.make_command()
				except Exception:
					pass
			finally:
				self._rush_after_id = None
		self._rush_schedule(on_timeout, int(self.turn_time_limit_sec * 1000))


if __name__ == '__main__':
	window = Tk()
	window.geometry("800x630")
	window.maxsize(800,630)
	window.minsize(800,630)
	window.title("Ludo Rush Mode")
	window.iconbitmap("Images/ludo_icon.ico")
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
	LudoRush(window, block_six_side, block_five_side, block_four_side, block_three_side, block_two_side, block_one_side)
	window.mainloop()
