# Homework 1 Solution
# Charles Franznick
# homework1_cwf170030.py

import sys
import pathlib
import re
import pickle


class Person:
    """creates a Person class with a display method 
    displays as following with 1 empty line between each employee
    Employee id: WH1234
        Smitty S Smith
        555-777-1212
    """
    def __init__(self, last, first, mi, id, phone):
        self.last = last
        self.first = first
        self.mi = mi
        self.id = id
        self.phone = phone

    def display(self):
        print("\nEmployee id: ", self.id)
        print("\t", self.first, self.mi, self.last)
        print("\t", self.phone)


def main():
    """
    Takes user input, opens/closes file, pickles and unpickles, and outputs data 
    """
    #make sure the user input a file path
    if len(sys.argv) < 2:
        print("User must define a file path. Exiting program.")
        quit()

    input_file_path = sys.argv[1]
    with open(pathlib.Path.cwd().joinpath(input_file_path), 'r') as f:
        text_in = f.read().splitlines()

    employees = process_lines(
        text_in[1:])  #ignore header line; returns dictionary of employees

    #pickle the employees
    pickle.dump(employees, open('employees.pickle', 'wb'))

    #read pickle back in
    employees_in = pickle.load(open('employees.pickle', 'rb'))

    #output employees
    print('\n\nEmployee list:')

    for emp_id in employees_in.keys():
        employees_in[emp_id].display()


def process_lines(text_in):
    """
    processes the data includng names, IDs, and phone numbers
    while correcting formats and asking for corrections
    returns dictionary of employees 
    """

    employees = {}  #create empty dictionary

    for line in text_in:
        last, first, mi, id, phone = line.split(',')

        # process the data
        # First, make sure names are in Capital Case
        if not last.istitle():
            old_last = last.lower()
            last = last[0].upper()
            last += (old_last[1:])
        if not first.istitle():
            old_first = first.lower()
            first = first[0].upper()
            first += (old_first[1:])
        if not mi.istitle():
            mi = mi.upper()
        if len(mi) < 1:
            mi = "X"

        # Second, modify id if necessary, using regex.  id should be 2 letters followed by 4 digits
        id = id.upper()
        id_pattern = "^[A-Z]{2}[0-9]{4}$"
        while not re.match(id_pattern, id) or id in employees:
            print("ID invalid or already in use: ", id)
            print("ID is two letters followed by 4 digits")
            id = input("Please enter a valid id: ").upper()

        # Third, modify phone number, if necessary, to be in form 999-999-9999
        phone = re.sub('[.]', '-', phone)
        phone = re.sub('[ ]', '-', phone)
        phone_pattern = "^[0-9]{3}[-]{1}[0-9]{3}[-]{1}[0-9]{4}$"
        while not re.match(phone_pattern, phone):
            print("Phone %s is invalid" % phone)
            print("Enter phone number in form 123-456-7890")
            phone = input("Enter phone number: ")
            phone = re.sub('[.]', '-', phone)
            phone = re.sub('[ ]', '-', phone)

        # Save employee in a the dictionary
        if id in employees:
            print(
                "Error: employee ID %s already in use. THIS ID WILL NOT BE ADDED TO DICTIONARY."
                % id)
        else:
            employees[id] = Person(last, first, mi, id, phone)

    return employees


if __name__ == "__main__":
    main()
