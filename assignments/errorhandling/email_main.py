from email_store import *

# Local instance of the email store.
EMAIL_STORE = EmailStore()


def view_emails():
    '''
    This function prints out each email in the store.
    '''
    count = 1
    print("\nEmails:")
    for email in EMAIL_STORE.emails:
        print(f"{count}) {email}")


def add_emails():
    '''
    This function uses a sentinal loop add email addresses to store.
    '''
    print("\nAdding emails...\n")
    user_input = input(
        "Enter first/last name separated by space ('Q to exit): ")
    while True:
        # check if user wants to exit.
        if user_input.lower() == "q":
            break
        # get first and last name from user input.
        user_input = user_input.lower().split(" ")
        first_name = user_input[0]
        last_name = user_input[1]

        # add the email to the store.
        email = EMAIL_STORE.add(first_name, last_name)
        print(f"Successfully added email to store '{email}'!")
        user_input = input(
            "Enter first/last name separated by space ('Q' to exit): ")


def remove_emails():
    '''
    This function uses a sentinal loop remove emails from the store.
    '''
    user_input = input("Enter user email to delete ('Q' to quit): ")
    while True:
        if user_input.lower() == "q":
            break
        # TODO use a try/except block to catch the exception thrown by the remove method.
        EMAIL_STORE.remove(user_input.lower())
        print(
            f"Successfully deleted the email '{user_input.lower()}' from store!")
        user_input = input("Enter user email to delete ('Q' to quit): ")


def main():

    # create instance of the email store.

    print("This program manages a local store for student emails.")
    print("\nMenu:")
    print("1) View")
    print("2) Add")
    print("3) Remove")
    print("Q) Quit")
    option = input("Enter operation: ").lower()
    while True:
        if option == "1":
            view_emails()
        elif option == "2":
            add_emails()
        elif option == "3":
            remove_emails()
        else:
            print("Exiting!")
            break
        print("This program manages a local store for student emails.")
        print("\nMenu:")
        print("1) View")
        print("2) Add")
        print("3) Remove")
        print("Q) Quit")
        option = input("Enter operation: ").lower()


main()