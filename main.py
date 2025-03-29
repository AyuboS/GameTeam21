import random


def generate_numbers():
    return random.sample([num for num in random.sample(range(20000, 30001), 1000) if num % 6 == 0], 5)


def minimax(number, depth, is_maximizing, alpha=None, beta=None, use_alpha_beta=False):
    if number <= 10:
        return 0

    best_score = float('-inf') if is_maximizing else float('inf')

    valid_moves = [choice for choice in [2, 3] if number % choice == 0]
    if not valid_moves:
        return 0

    for choice in valid_moves:
        new_number = number // choice
        score = minimax(new_number, depth + 1, not is_maximizing, alpha, beta, use_alpha_beta)

        if is_maximizing:
            best_score = max(best_score, score)
            if use_alpha_beta:
                alpha = max(alpha, best_score)
        else:
            best_score = min(best_score, score)
            if use_alpha_beta:
                beta = min(beta, best_score)

        if use_alpha_beta and beta <= alpha:
            break

    return best_score


def computer_move(number, algorithm):
    best_choice = None
    best_score = float('-inf')

    valid_moves = [choice for choice in [2, 3] if number % choice == 0]
    if not valid_moves:
        return None

    for choice in valid_moves:
        new_number = number // choice
        score = minimax(new_number, 0, False, float('-inf'), float('inf'), algorithm == 'alpha-beta')

        if score > best_score:
            best_score = score
            best_choice = choice

    return best_choice


def play_game():
    numbers = generate_numbers()
    print("Generated numbers:", numbers)
    chosen_number = int(input("Choose a number from the list: "))

    if chosen_number not in numbers:
        print("Invalid choice.")
        play_again = input("Do you want to play again? (yes/no)").strip().lower()
        if play_again == "yes":
            play_game()
        else:
            return

    player1_score = 0
    player2_score = 0
    game_bank = 0
    current_number = chosen_number

    human_first = input("Do you want to play first? (yes/no): ").strip().lower() == "yes"
    algorithm_choice = input("Choose algorithm (minimax/alpha-beta): ").strip().lower()

    turn = 0 if human_first else 1

    while current_number > 10:
        print(f"Current number: {current_number}")
        if current_number % 2 != 0 and current_number % 3 != 0:
            print("No valid moves left. Game over!")
            break

        if turn == 0:
            choice = int(input("Divide by (2 or 3): "))
        else:
            choice = computer_move(current_number, algorithm_choice)
            if choice is None:
                print("Computer has no valid move. Game over!")
                break
            print(f"Computer chooses to divide by {choice}")

        if choice not in [2, 3] or current_number % choice != 0:
            print("Invalid move. Try again.")
            continue

        current_number //= choice

        if current_number % 10 in [0, 5]:
            game_bank += 1

        if choice == 2:
            if turn == 0:
                player2_score += 2
            else:
                player1_score += 2
        else:
            if turn == 0:
                player1_score += 3
            else:
                player2_score += 3

        turn = 1 - turn  # Switch turns

    print(f"Game over! Final number: {current_number}")
    if turn == 0:
        player1_score += game_bank
    else:
        player2_score += game_bank

    print(f"Final Scores - Player 1: {player1_score}, Player 2: {player2_score}")

    if player1_score > player2_score:
        print("Player 1 wins!")
    elif player2_score > player1_score:
        print("Player 2 wins!")
    else:
        print("It's a draw!")


play_game()
