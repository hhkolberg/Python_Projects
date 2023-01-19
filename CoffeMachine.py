MENU = {
    "espresso": {
        "ingredients": {
            "water": 50,
            "coffee": 18,
        },
        "cost": 1.5,
    },
    "latte": {
        "ingredients": {
            "water": 200,
            "milk": 150,
            "coffee": 24,
        },
        "cost": 2.5,
    },
    "cappuccino": {
        "ingredients": {
            "water": 250,
            "milk": 100,
            "coffee": 24,
        },
        "cost": 3.0,
    }
}

resources = {
    "water": 300,
    "milk": 200,
    "coffee": 100,
}


def enough_money(chose):
    return MENU[chose]["cost"]


def calculation(quarters, dimes, nickles, pennies, cost):
    qr = quarters * 0.25
    dr = dimes * 0.10
    nr = nickles * 0.05
    pr = pennies * 0.01
    finale_sum = qr + dr + nr + pr
    return finale_sum


def repay(sum, cost):
    repay_sum = sum - cost
    return repay_sum


def Update_stock(chose, MENU, resources):
    water_amount = MENU[chose]["ingredients"]["water"]
    coffee_amount = MENU[chose]["ingredients"]["coffee"]
    if chose == "latte" or chose == "cappuccino":
        milk_amount = MENU[chose]["ingredients"]["milk"]
    resources["water"] -= water_amount
    resources["milk"] -= milk_amount
    resources["coffee"] -= coffee_amount
    return resources


def check_resources(chose, MENU, resources):
    for key in MENU[chose]["ingredients"]:
        if key in resources:
            if resources[key] > MENU[chose]["ingredients"][key]:
                return True
            else:
                return False


InStock = True
while InStock:
    chose = input("What would you like? (espresso/latte/cappuccino):")
    check_result = check_resources(chose, MENU, resources)
    if check_result == False:
        print("Sorry, not enough resources")
        continue
    else:
        print("Please insert coins.")
        quarters = int(input("how many quarters?: "))
        dimes = int(input("how many dimes?: "))
        nickles = int(input("how many nickles?: "))
        pennies = int(input("how many pennies?: "))

        enough_money(chose)
        cost = enough_money(chose)
        SUM = calculation(quarters, dimes, nickles, pennies, cost)
        sum = round(SUM, 3)

        if sum == cost:
            Update_stock(chose, MENU, resources)
        if sum > cost:
            repay(sum, cost)
            payback = round(repay(sum, cost))
            print(f"Here is {payback}€ in change.")
            Update_stock(chose, MENU, resources)
            print(f'Here is your {chose} ☕️. Enjoy!')

        if sum < cost:
            print("Sorry that's not enough money. Money refunded.")