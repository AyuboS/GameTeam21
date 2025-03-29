import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import math

class GameNode:
    def __init__(self, number, player1_score, player2_score, game_bank, depth, is_maximizing):
        self.number = number
        self.player1_score = player1_score
        self.player2_score = player2_score
        self.game_bank = game_bank
        self.depth = depth
        self.is_maximizing = is_maximizing
        self.children = []
        self.best_move = None

    def generate_children(self, current_player_turn, human_is_player1):
        self.children = []
        ai_is_player1 = not human_is_player1
        ai_turn = (current_player_turn == 0 and ai_is_player1) or \
                  (current_player_turn == 1 and not ai_is_player1)

        for move in [2, 3]:
            if self.number % move == 0:
                new_number = self.number // move
                new_p1_score = self.player1_score
                new_p2_score = self.player2_score
                new_bank = self.game_bank

                if move == 2:
                    if current_player_turn == 0:
                        new_p2_score += 2
                    else:
                        new_p1_score += 2
                elif move == 3:
                    if current_player_turn == 0:
                        new_p1_score += 3
                    else:
                        new_p2_score += 3

                if new_number % 10 == 0 or new_number % 5 == 0:
                    new_bank += 1

                child_node = GameNode(
                    new_number,
                    new_p1_score,
                    new_p2_score,
                    new_bank,
                    self.depth + 1,
                    not self.is_maximizing
                )
                self.children.append((move, child_node))

def heuristic_evaluation(node, human_is_player1):
    ai_score = node.player2_score if human_is_player1 else node.player1_score
    human_score = node.player1_score if human_is_player1 else node.player2_score

    if node.number <= 10:
        final_ai_score = ai_score
        final_human_score = human_score

        if not node.is_maximizing:
            final_ai_score += node.game_bank
        else:
            final_human_score += node.game_bank

        score_diff = final_ai_score - final_human_score
        if score_diff > 0:
            return 1000 + score_diff
        elif score_diff < 0:
            return -1000 + score_diff
        else:
            return 0

    score = ai_score - human_score
    score += node.game_bank

    if score > 0:
         score += (30000 - node.number) / 1000
    elif score < 0:
         score -= (30000 - node.number) / 1000

    can_ai_add_3 = False
    can_human_add_3 = False
    for move in [2, 3]:
        if node.number % move == 0:
            if node.is_maximizing:
                if move == 3: can_ai_add_3 = True
            else:
                 if move == 3: can_human_add_3 = True

    if can_ai_add_3: score += 3
    if can_human_add_3: score -= 3

    return score

def minimax(node, depth, alpha, beta, use_alpha_beta, human_is_player1, max_depth=5):
    current_player_turn = (node.depth % 2 == 0) if human_is_player1 else (node.depth % 2 != 0)

    if node.number <= 10 or depth >= max_depth:
        return heuristic_evaluation(node, human_is_player1)

    ai_turn = node.is_maximizing
    actual_turn = -1
    if human_is_player1:
        actual_turn = 1 if ai_turn else 0
    else:
        actual_turn = 0 if ai_turn else 1

    node.generate_children(actual_turn, human_is_player1)

    if not node.children:
        return -math.inf if node.is_maximizing else math.inf

    if node.is_maximizing:
        best_score = -math.inf
        best_move_for_node = node.children[0][0] if node.children else None
        for move, child in node.children:
            score = minimax(child, depth + 1, alpha, beta, use_alpha_beta, human_is_player1, max_depth)
            if score > best_score:
                best_score = score
                best_move_for_node = move
            if use_alpha_beta:
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
        if depth == 0:
             node.best_move = best_move_for_node
        return best_score
    else:
        best_score = math.inf
        best_move_for_node = node.children[0][0] if node.children else None
        for move, child in node.children:
            score = minimax(child, depth + 1, alpha, beta, use_alpha_beta, human_is_player1, max_depth)
            if score < best_score:
                best_score = score
                best_move_for_node = move # AI tracks human's assumed best move here
            if use_alpha_beta:
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
        return best_score


def get_computer_move(current_number, p1_score, p2_score, bank, algorithm, human_is_player1, max_depth=4):
    start_time = time.time()
    ai_is_player1 = not human_is_player1

    root = GameNode(current_number, p1_score, p2_score, bank, 0, True)

    use_alpha_beta = (algorithm == 'alpha-beta')
    alpha = -math.inf
    beta = math.inf

    best_score = minimax(root, 0, alpha, beta, use_alpha_beta, human_is_player1, max_depth)

    end_time = time.time()
    move_time = end_time - start_time

    if root.best_move is None and root.children:
         root.best_move = root.children[0][0]
    elif not root.children and current_number > 10:
         if current_number % 2 == 0: root.best_move = 2
         elif current_number % 3 == 0: root.best_move = 3
         else: return None, move_time
    elif not root.children:
        return None, move_time


    return root.best_move, move_time

class NumberGameGUI:
    def __init__(self, master):
        self.master = master
        master.title("Number Division Game")
        master.geometry("700x550")

        self.current_number = 0
        self.player1_score = 0
        self.player2_score = 0
        self.game_bank = 0
        self.human_is_player1 = True
        self.current_turn = 0
        self.game_active = False
        self.selected_algorithm = "minimax"
        self.ai_move_time_total = 0
        self.ai_moves_count = 0

        self.config_frame = tk.LabelFrame(master, text="Game Setup", padx=10, pady=10)
        self.config_frame.pack(padx=10, pady=10, fill='x')

        num_sel_frame = tk.Frame(self.config_frame)
        num_sel_frame.pack(fill='x')
        tk.Label(num_sel_frame, text="Choose Starting Number:", width=20, anchor='w').pack(side=tk.LEFT)
        self.numbers_var = tk.StringVar()
        self.numbers_combobox = ttk.Combobox(num_sel_frame, textvariable=self.numbers_var, state='readonly', width=10)
        self.numbers_combobox.pack(side=tk.LEFT, padx=5)
        self.regenerate_button = tk.Button(num_sel_frame, text="⟳", command=self.regenerate_numbers, width=3)
        self.regenerate_button.pack(side=tk.LEFT)
        self.update_numbers_dropdown()

        algo_frame = tk.Frame(self.config_frame)
        algo_frame.pack(fill='x')
        tk.Label(algo_frame, text="Choose Algorithm:", width=20, anchor='w').pack(side=tk.LEFT)
        self.algorithm_var = tk.StringVar(value="minimax")
        self.algorithm_radio_minimax = tk.Radiobutton(
            algo_frame, text="Minimax", variable=self.algorithm_var, value="minimax", command=self.update_algorithm)
        self.algorithm_radio_alpha_beta = tk.Radiobutton(
            algo_frame, text="Alpha-Beta", variable=self.algorithm_var, value="alpha-beta", command=self.update_algorithm)
        self.algorithm_radio_minimax.pack(side=tk.LEFT, padx=5)
        self.algorithm_radio_alpha_beta.pack(side=tk.LEFT, padx=5)

        player_frame = tk.Frame(self.config_frame)
        player_frame.pack(fill='x')
        tk.Label(player_frame, text="Who Plays First?", width=20, anchor='w').pack(side=tk.LEFT)
        self.first_player_var = tk.StringVar(value="human")
        self.first_player_human = tk.Radiobutton(
            player_frame, text="Human", variable=self.first_player_var, value="human")
        self.first_player_computer = tk.Radiobutton(
            player_frame, text="Computer", variable=self.first_player_var, value="computer")
        self.first_player_human.pack(side=tk.LEFT, padx=5)
        self.first_player_computer.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(self.config_frame, text="Start Game", command=self.start_game, width=15)
        self.start_button.pack(pady=10)

        self.status_frame = tk.LabelFrame(master, text="Game Status", padx=10, pady=10)
        self.status_frame.pack(padx=10, pady=5, fill='x')
        self.current_number_label = tk.Label(self.status_frame, text="Current Number: -", font=("Arial", 16))
        self.current_number_label.pack()
        self.turn_label = tk.Label(self.status_frame, text="Turn: -", font=("Arial", 10))
        self.turn_label.pack()

        self.scores_frame = tk.LabelFrame(master, text="Scores", padx=10, pady=10)
        self.scores_frame.pack(padx=10, pady=5, fill='x')
        self.player1_score_label = tk.Label(self.scores_frame, text="Player 1 (Human): 0", font=("Arial", 12))
        self.player1_score_label.pack()
        self.player2_score_label = tk.Label(self.scores_frame, text="Player 2 (Computer): 0", font=("Arial", 12))
        self.player2_score_label.pack()
        self.bank_score_label = tk.Label(self.scores_frame, text="Bank: 0", font=("Arial", 12))
        self.bank_score_label.pack(pady=5)

        self.moves_frame = tk.LabelFrame(master, text="Your Move", padx=10, pady=10)
        self.moves_frame.pack(padx=10, pady=10, fill='x')
        self.move_buttons = []

    def update_numbers_dropdown(self):
        numbers = self._generate_numbers()
        self.numbers_combobox['values'] = [str(num) for num in numbers]
        if numbers:
            self.numbers_combobox.set(str(numbers[0]))

    def _generate_numbers(self):
         count = 0
         generated = []
         attempts = 0
         max_attempts = 20000
         while count < 5 and attempts < max_attempts:
             num = random.randint(20000, 30000)
             if num % 6 == 0 and num not in generated:
                 generated.append(num)
                 count += 1
             attempts += 1

         while count < 5:
             fallback_num = 20004 + count * 6
             if fallback_num <= 30000 and fallback_num not in generated:
                 generated.append(fallback_num)
             else:
                 fb_attempts = 0
                 while fb_attempts < 100:
                     num = random.randint(20000, 30000)
                     if num % 6 == 0 and num not in generated:
                         generated.append(num)
                         break
                     fb_attempts += 1
                 if len(generated) < count + 1: break
             count += 1

         return generated

    def regenerate_numbers(self):
        """Regenerates the list of numbers in the dropdown"""
        self.update_numbers_dropdown()

    def update_algorithm(self):
        self.selected_algorithm = self.algorithm_var.get()

    def toggle_config_widgets(self, state):
        widget_state = tk.DISABLED if state == 'disable' else tk.NORMAL
        combobox_state = tk.DISABLED if state == 'disable' else 'readonly'

        self.numbers_combobox.config(state=combobox_state)
        self.regenerate_button.config(state=widget_state)
        self.algorithm_radio_minimax.config(state=widget_state)
        self.algorithm_radio_alpha_beta.config(state=widget_state)
        self.first_player_human.config(state=widget_state)
        self.first_player_computer.config(state=widget_state)
        self.start_button.config(state=widget_state)

    def start_game(self):
        if not self.numbers_var.get():
             messagebox.showerror("Error", "No starting number selected or generated.")
             return
        try:
            self.current_number = int(self.numbers_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please select a valid starting number.")
            return

        self.player1_score = 0
        self.player2_score = 0
        self.game_bank = 0
        self.human_is_player1 = (self.first_player_var.get() == "human")
        self.current_turn = 0
        self.selected_algorithm = self.algorithm_var.get()
        self.game_active = True
        self.ai_move_time_total = 0
        self.ai_moves_count = 0

        self.toggle_config_widgets('disable')
        self.update_score_labels()
        self.handle_turn()

    def update_display(self):
        if not self.game_active:
             self.current_number_label.config(text=f"Current Number: {self.current_number}")
             self.turn_label.config(text="Game Over")
             self.update_score_labels()
             return

        self.current_number_label.config(text=f"Current Number: {self.current_number}")
        self.bank_score_label.config(text=f"Bank: {self.game_bank}")
        self.update_score_labels()

        is_human_turn = (self.current_turn == 0 and self.human_is_player1) or \
                        (self.current_turn == 1 and not self.human_is_player1)

        if is_human_turn:
            turn_text = "Your Turn (Player {})".format(self.current_turn + 1)
            self.moves_frame.config(text="Your Move")
        else:
            turn_text = "Computer's Turn (Player {})".format(self.current_turn + 1)
            self.moves_frame.config(text="Computer Thinking...")

        self.turn_label.config(text=turn_text)

    def update_score_labels(self):
        p1_tag = "(Human)" if self.human_is_player1 else "(Computer)"
        p2_tag = "(Computer)" if self.human_is_player1 else "(Human)"
        self.player1_score_label.config(text=f"Player 1 {p1_tag}: {self.player1_score}")
        self.player2_score_label.config(text=f"Player 2 {p2_tag}: {self.player2_score}")
        self.bank_score_label.config(text=f"Bank: {self.game_bank}")


    def clear_move_buttons(self):
        for widget in self.move_buttons:
            widget.destroy()
        self.move_buttons = []

    def update_move_buttons(self):
        self.clear_move_buttons()
        possible_moves = []
        button_frame = tk.Frame(self.moves_frame)
        button_frame.pack()
        self.move_buttons.append(button_frame)

        if self.current_number > 10 and self.current_number % 2 == 0:
            possible_moves.append(2)
            button2 = tk.Button(button_frame, text="Divide by 2", command=lambda div=2: self.handle_human_move(div), width=15)
            button2.pack(side=tk.LEFT, padx=5, pady=5)
            self.move_buttons.append(button2)

        if self.current_number > 10 and self.current_number % 3 == 0:
            possible_moves.append(3)
            button3 = tk.Button(button_frame, text="Divide by 3", command=lambda div=3: self.handle_human_move(div), width=15)
            button3.pack(side=tk.LEFT, padx=5, pady=5)
            self.move_buttons.append(button3)

        if self.current_number > 10 and not possible_moves:
             self.end_game("No valid moves left.")


    def handle_human_move(self, divisor):
        if not self.game_active: return
        is_human_turn = (self.current_turn == 0 and self.human_is_player1) or \
                        (self.current_turn == 1 and not self.human_is_player1)
        if not is_human_turn: return

        self.clear_move_buttons()
        self.process_move(divisor)

    def handle_computer_move(self):
        self.clear_move_buttons()
        self.update_display()
        self.master.update_idletasks()

        move, move_time = get_computer_move(
            self.current_number,
            self.player1_score,
            self.player2_score,
            self.game_bank,
            self.selected_algorithm,
            self.human_is_player1
        )
        self.ai_move_time_total += move_time
        self.ai_moves_count += 1

        if move is None:

             if self.current_number <= 10:
                 self.end_game()
             else:
                 self.end_game("Computer has no valid moves.")
             return

        delay_ms = 300

        self.master.after(delay_ms, lambda m=move: self.process_move(m))


    def process_move(self, divisor):
        if not self.game_active: return

        if self.current_number % divisor != 0:
            print(f"Error: Attempted to divide {self.current_number} by {divisor}")
            self.end_game(f"Internal Error: Invalid division attempted ({divisor})")
            return

        new_number = self.current_number // divisor

        if divisor == 2:
            if self.current_turn == 0: self.player2_score += 2
            else: self.player1_score += 2
        elif divisor == 3:
            if self.current_turn == 0: self.player1_score += 3
            else: self.player2_score += 3

        if new_number % 10 == 0 or new_number % 5 == 0:
            self.game_bank += 1

        self.current_number = new_number
        self.current_turn = 1 - self.current_turn

        self.handle_turn()


    def handle_turn(self):
        if not self.game_active: return

        if self.current_number <= 10:
            self.end_game()
            return

        self.update_display()

        is_human_turn = (self.current_turn == 0 and self.human_is_player1) or \
                        (self.current_turn == 1 and not self.human_is_player1)

        if is_human_turn:
            self.update_move_buttons()
        else:
            self.handle_computer_move()

    def end_game(self, reason=None):
        # Prevent multiple calls
        if not self.game_active: return
        self.game_active = False

        self.clear_move_buttons()

        last_player_turn = 1 - self.current_turn
        if self.game_bank > 0:
            if last_player_turn == 0:
                 self.player1_score += self.game_bank
            else: self.player2_score += self.game_bank
            self.game_bank = 0

        self.update_display()

        p1_final = self.player1_score
        p2_final = self.player2_score

        p1_tag = "P1 (Human)" if self.human_is_player1 else "P1 (Computer)"
        p2_tag = "P2 (Computer)" if self.human_is_player1 else "P2 (Human)"

        result_message = f"Game Over! Final Number: {self.current_number}\n\n"
        if reason:
             result_message += f"Reason: {reason}\n\n"
        result_message += f"Final Scores:\n"
        result_message += f"{p1_tag}: {p1_final}\n"
        result_message += f"{p2_tag}: {p2_final}\n\n"

        winner = ""
        if p1_final > p2_final:
            winner = "Player 1 wins!"
        elif p2_final > p1_final:
            winner = "Player 2 wins!"
        else:
            winner = "It's a draw!"

        result_message += winner

        if self.ai_moves_count > 0:
             avg_time = self.ai_move_time_total / self.ai_moves_count
             result_message += f"\n\nAvg AI move time: {avg_time:.4f}s"


        self.master.after(100, lambda: messagebox.showinfo("Game Over", result_message))
        self.toggle_config_widgets('enable')
        self.turn_label.config(text="Game Over. Ready for setup.")


def main():
    root = tk.Tk()
    game_gui = NumberGameGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()