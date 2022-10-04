def start():

    answer = "ostrich"
    guess_limit = 3
    guess_count = 0

    print("Guess the animal, you have 3 guesses!")
    while guess_count < guess_limit:
        guess = input("Enter Animal: ").lower()
        guess_count += 1
        if guess == answer:
            print("Correct! Congradulations!")
            break
        elif guess == "quit":
            print("leaving game...")
            break
        else:
            print("Incorrect! Try again")


start()
