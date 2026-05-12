


# - Menus - #

# - Main Menu - #

def main_menu():
    option = int(input('''\n\tMain Menu
1. See our Products
2. Register
3. Login
4. Exit
----------------- '''))
    return option

# - Admin Menu - #

def admin_menu():
    option = int(input('''\n\tWhat do you want to do?
1. Create a new Product
2. Update a Product
3. Delete a Product
4. See all Products
5. See Pending Orders
6. See Users Registered
7. Exit
----------------------- '''))
    return option

# - Cx Menu - #

def customer_menu() -> int:
    option = int(input('''\nWhat do you want to do?
1. See products
2. See the Cart
3. See Your Orders
4. Exit
--------------------- '''))
    return option

# - Exit Menu: this will help when you will be requested if you want to use another function -#

def exitMenu():
    print("\nDo you want to do something else?")
    option = int(input("1. Yes\n" +
                      "2. Exit\n------- "))
    if option == 1:
            condition = True
    elif option == 2:
        print("""\n\tThank you for using our services!\n
Enjoy the rest of your day :)\n""")
        condition = False
    else:
        condition = True
    return condition

def product_menu(email:str):
    print('\nShowing all products listed...\n')
    #show_products(product_path_csv)
    #from user_data_db import validate_if_user_exist
    #user_info, validation = validate_if_user_exist(email)
    #if validation:
    #   if user_info['role'] == 'cx':
    #        buy_or_not = int(input('''\nDo you want to buy something?
#1. Yes
#2. No
#---------------- '''))
            #if buy_or_not == 1: 
            #    product_id = int(input('\nWhat is the ID from the product that you want to add?\n------------- '))
            #    product_class.buy_product(email,product_id)
            #elif buy_or_not == 2:
            #    print() # Exit
            #else:
                #raise ValueError('Incorrect Option')