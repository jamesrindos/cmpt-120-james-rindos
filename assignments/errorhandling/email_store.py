from genericpath import exists


class EmailStore:

    def __init__(self):
        '''
        Constructor method.
        '''
        self.emails = []

    def exists(self, email):
        '''
        Method that checks if an email exists in store.
        '''
        return email in self.emails

    def add(self, first_name, last_name):
        '''
        Method that adds a new email to the store.
        The email address is of the format {first_name}.{last_name}{count}@marist.edu

        @return the email that was added.
        '''
        email = None
        count = 1
        # TODO if either first_name or last_name is None raise an exception
        # try:
        email = first_name + "." + last_name + str(count) + "@marist.edu"
        # print("success!")
        # except Exception as first_name:
        #     print("Please enter both a first and a last name")
        # except Exception as last_name:
        #     print("Please enter both a first and a last name")

        # TODO use a while loop to construct email from first_name and last_name and check if it exists.
        # TODO if generated email exists, increment count.
        # TODO if generated email doesn't exist, add it to the collection of emails (self.emails).
        unique = True
        while unique:
            email = first_name + "." + last_name + str(count) + "@marist.edu"
            if email in self.emails:
                count = count + 1
            else:
                self.emails.append(email)
                unique = False

        return email

    def remove(self, email):
        '''
        Method that removes an email from the store.
        '''
        # TODO if email doesn't exist, raise an exception.
        try:
            self.emails.remove
        except:
            raise ("email not found")

        self.emails.remove(email)
