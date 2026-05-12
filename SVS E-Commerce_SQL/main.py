
'''
I'll be creating an e-commerce

so far what I want is

Display All products once you get in --> A DB that display this info

Login and Register depending on the user

Login as an Admin: An admin cannot Register, an Admin is already set up because the email is already in the DB
    The user should be already created: An Admin should be assign
        Login with --> User = Email, Password
        Then display the Admin menu
            Menu: Create, Read, Update, Delete
                Create: Request info from the product: Name, Description, Price, Stock, Discount? --> Added if all the info is fill out
                Read: See all products
                Update: Change all the info, request via menu what they want to change
                Delete :)
                Approve Orders --> If theres a Pending Order, display a message when the admin login --> Approve | Not
                See the users registered
            They can see the products and the pay page, but cannot buy
            

Register: Only Users
    Request info: Name, Last Name, Email, Phone#, Address, Password
    Then let the User add products to the cart and buy things
Login: User
    Ask for Email|Phone# and Password
    Menu: See products | See the cart | See orders: Provide if it's in Process or Deliver

No categories for products (we could consider this for v2, adding a columm is easy)
Products: All the product info + User choose: Add it to the cart | Back
Cart --> This will display, Product Added, Price, Qty and Total + Buy Option | Back
Buy Page --> Confirm Address to the User, display Product Name, Qty & Price ** Important
    If Customer pay (no payment method option so far), save the order

The stucture of this will be like the following:

ecommerce/
├─ models.sql         # crea tablas y constraints
├─ init_db.py         # ejecuta models.sql y seed admin
├─ db.py              # helpers de conexión y consultas
├─ app.py             # aplicación de consola (menús y lógica)
├─ requirements.txt
└─ README.md

'''

# Imports # 

import login
import menus

# - Vars - #

# How should I add the DB?
exit_option = True

# - Main Program - #

while exit_option:
    try:
        condition = True
        print('\n\tWelcome to our SVS Shop\n\nHere are the options available\n')
        login_validation = int(input('Do you want to loging?\n1. Yes\n2. No\n----------- '))
        if login_validation == 1:
            email = str(input('\nWhat is your email?\n------------ '))
            temp_password = input('\nWhat is your password?\n-------- ')
            while(condition):
                if not login.login(email, temp_password): break
        else: 
            while(condition):  
                option = menus.main_menu()
                if option == 1: 
                    page_size=50
                    #product_data_db.show_products(PRODUCT_PATH_CSV, page_size)
                    if menus.exitMenu() == False:
                        condition=False
                        exit_option=False
               # elif option == 2: new_user()
                elif option == 3: 
                    email = input('\nWhat is your E-mail?\n------------------- ')
                    temp_password = input('What is your password?\n-------- ')
                    if not login.login(email, temp_password): condition = False
                elif option == 4:
                    condition = False
                    exit_option = False
                    print('\nThank you for using our services!\n\tEnjoy the rest of your day :)\n\t')
                else:
                    raise Exception

    except Exception as e:
        print(f'\nAn error occurred: {e}')
        print('Restarting Menu... \n')
    finally:
        if exit_option != False:
            exit_option = menus.exitMenu()
        