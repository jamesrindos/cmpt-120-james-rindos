class Product:

    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

# b. Add methods to your class that takes an integer count and determines whether
# that many of the product are in stock.
    def quantity(self, count):
        return count <= self.stock

# c. Add another method that takes a count and returns the total cost of that many
# of the product.
    def cost(self, count):
        return self.price * count

# d. Finally, add a method that takes a count and removes that many of the product
# from the stock.
    def remaining(self, count):
        return self.stock - count
# 2. Next, replace the three product lists with a single list of Product instances.

def main():

    p1 = Product("Ultrasonic range finger", 2.50, 4)
    p2 = Product("Servo motor", 14.99, 10)
    p3 = Product("Servo controller", 44.95, 5)
    p4 = Product("Microcontroller Board", 34.95, 7)
    p5 = Product("Laser range finder", 149.99, 2)
    p6 = Product("Lithium polymer battery", 8.99, 8)
    products = [p1, p2, p3, p4, p5, p6]
# 3. Modify the rest of the code to correctly use the attributes and methods of the Products
# in the list.
    print(products[4].quantity(4))
    print(products[2].cost(2))
    print(products[3].remaining(3))
    
# 4. Test your program as you go and fix any syntax or logic errors in order to get it working
# correctly.
# 5. Add, commit, and push your final version.
main()