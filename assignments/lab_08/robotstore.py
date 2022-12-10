product_names = [ "Ultrasonic range finger",
                 "Servo motor",
                 "Servo controller",
                 "Microcontroller Board",
                 "Laser range finder",
                 "Lithium polymer battery" ]

product_prices = [ 2.50, 14.99, 44.95, 34.95, 149.99, 8.99 ]
product_quantities = [ 4, 10, 5, 7, 2, 8 ]

def print_stock():
    print("\nAvailable Products")
    print("------------------")
    for i in range(0, len(product_names)):
        if product_quantities[i] > 0:
            print(str(i) + ")", product_names [i], "$", product_prices[i])
    print()
    
def main():
    cash = float(input("How much money do you have? $"))
    while cash > 0:
        print_stock()
        vals = input("Enter product ID and quantity you wish to buy: ").split(" ")
        if vals[0] == "quit": break
        
        prod_id = int(vals[0])
        count = int(vals[1])
        
        if product_quantities [prod_id] >= count:
            if cash >= product_prices[prod_id]:
                product_quantities [prod_id] * count
                cash -= product_prices [prod_id] * count
                print("You purchased", count, product_names[prod_id] + ".")
                print("You have $", "{0:.2f}".format(cash), "remaining.")
            else:
                print("Sorry, you cannot afford that product.")
        else:
            print("Sorry, we are sold out of", product_names[prod_id])
            
main()