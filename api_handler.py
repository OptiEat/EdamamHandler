import urllib.request, ujson


app_id = ["290dd3fc", "dbbc8240", "98b8c38a", "05ffdf1f", "4d4a14a1", "005ecd18", "11c9b707", "3eaeb931", "cc223b97", "fb3e6780", "0f954f5f", "9b4a0665"]
api_key = [
    "e7f2e085f4e7cb93690ae475fcdf203b", 
    "7f1a399c48313f316d208b33e0d56b9d",
    "e4b94dc003b4c7e97d8d96b66bd31e22",
    "2df4ad0492933516ff6edd00ee4ef176", 
    "cd106303c53916c98fd47d9751f922d8", 
    "f778db93648ba4cd94929ca4472cdcc2",
    "358fc6a15673f4e4362e77a363c9ffe2",
    "6a883794ff84d76393c8aa183b2f439e",
    "aa6876ce669b270514c1b05249c3e5ba",
    "c627c795d1fc4a3ca80be5348e737c89",
    "04358755126356dbfcbc8399b839d35c",
    "76e85add0b9f1b27a61eae13b7c02231",
]
api_counter = -1

def _read_json(url):
    with urllib.request.urlopen(url) as url2:
        data = ujson.loads(url2.read().decode())
        return data


def _compose_url(ingredients, allowed_extra_ingredients):
    global api_counter
    api_counter += 1
    return u"https://api.edamam.com/search?q={0}&app_id={1}&app_key={2}&ingr={3}&to=100".format(
        ",".join(ingredients),
        app_id[api_counter // 5],
        api_key[api_counter // 5],
        len(ingredients) + allowed_extra_ingredients
    )


def _is_ingredient_in_recipe(ingredient, recipe_ingredients):
    for counter, item in enumerate(recipe_ingredients, start=0):
        item = item["text"].lower()
        if ingredient in item:
            return counter
    return -1

def _get_weight_for_ingredient(ingredient, recipe_ingredients):
    for item in recipe_ingredients:
        text = item["text"].lower()
        if ingredient in text:
            return item["weight"]
    

def chose_recipe_from_data(data, ingredients):
    ingredients = [x.lower() for x in ingredients]
    for recipe in data["hits"]:
        recipe = recipe["recipe"]
        recipe_ingredients = recipe["ingredients"].copy()
        foundRecipe = True
        for ingredient in ingredients:
            index = _is_ingredient_in_recipe(ingredient, recipe_ingredients)
            if index == -1:
                foundRecipe = False
                break
            else:
                del recipe_ingredients[index]
        if foundRecipe:
            return recipe
    return None


def get_weight_for_recipe(recipe, ingredients):
    recipe_ingredients = recipe["ingredients"]
    return [_get_weight_for_ingredient(ingredient, recipe_ingredients) for ingredient in ingredients]
    
            
def find_recipe(ingredients, margin):
    data = _read_json(_compose_url(ingredients, margin))
    return chose_recipe_from_data(data, ingredients)


def find_meals(groceries):
    """
    This function take as input a list of list. Each element is a list like the following:
    ["ingredient_name", "expiration_date - today", "grams"]
    """
    groceries = sorted(groceries, key = lambda x: x[1])
    recipes = []
    while len(groceries) >= 0:    
        ingredients_names = [x[0] for x in groceries]
        ingredients_grams = [x[2] for x in groceries]
        ingredients_quantity_types = [x[3] for x in groceries]

        i = 1       
        recipe = None
        ingredients = None
        while not recipe and i < len(groceries):
            ingredients = [ingredients_names[0], ingredients_names[i]]
            margin = 0
            while margin < 2:
                recipe = find_recipe(ingredients, margin)
                if recipe:
                    break
                margin += 1
            i += 1
        i -= 1
        if not recipe:
            break
        ingredients_usage = get_weight_for_recipe(recipe, ingredients)
        first_ingredient = ingredients_usage[0] if ingredients_usage[0] > 0 else 0.00001
        second_ingredient = ingredients_usage[1] if ingredients_usage[1] > 0 else 0.00001
        first_ratio = ingredients_grams[0] / first_ingredient
        second_ratio = ingredients_grams[i] / second_ingredient
        if first_ratio < second_ratio:
            to_remove = ingredients_grams[0] * ingredients_usage[1] / ingredients_usage[0]
            groceries[0][2] -= ingredients_grams[0]
            groceries[i][2] -= to_remove
            recipe["effectiveWeight"] = [{ingredients_names[0]: compute_weight(ingredients_quantity_types[0], ingredients_grams[0])}, {ingredients_names[i]: compute_weight(ingredients_quantity_types[i], to_remove)}]
        else:
            to_remove = ingredients_grams[1] * ingredients_usage[0] / ingredients_usage[1]
            groceries[i][2] -= ingredients_grams[1]
            groceries[0][2] -= to_remove
            recipe["effectiveWeight"] = [{ingredients_names[0]: compute_weight(ingredients_quantity_types[0], to_remove)}, {ingredients_names[i]: compute_weight(ingredients_quantity_types[1], ingredients_grams[1])}]

        recipes.append(recipe)
        if groceries[i][2] <= 0:
            del groceries[i]
        if groceries[0][2] <= 0:
            del groceries[0]
    
    return recipes, groceries


def compute_grams(quantity_type, quantity):
    if quantity_type == "Ounces":
        return quantity * 28
    elif quantity_type == "Fl Oz":
        return quantity * 30
    elif quantity_type == "Pounds":
        return quantity * 454
    elif quantity_type == "Count":
        return quantity * 100
    elif quantity_type == "Jars":
        return quantity * 350
    elif quantity_type == "Boxes":
        return quantity * 400
    elif quantity_type == "Gallons":
        return quantity * 3785
    elif quantity_type == "Packs":
        return quantity * 400
    else:
        return quantity

def compute_weight(quantity_type, grams):
    if quantity_type == "Ounces":
        return grams / 28
    elif quantity_type == "Fl Oz":
        return grams / 30
    elif quantity_type == "Pounds":
        return grams / 454
    elif quantity_type == "Count":
        return grams / 100
    elif quantity_type == "Jars":
        return grams / 350
    elif quantity_type == "Boxes":
        return grams / 400
    elif quantity_type == "Gallons":
        return grams / 3785
    elif quantity_type == "Packs":
        return grams / 400
    else:
        return grams


def compute_recipes(data):
    global api_counter
    api_counter = -1
    dictionary = ujson.loads(data)
    groceries = []
    total_weight = 0
    temp_weight = 0
    for item in dictionary["Products"]:
        temp_weight = compute_grams(item["quantityType"], int(item["quantity"]))
        total_weight += temp_weight
        groceries.append([item["shortName"], int(item["expiration"]), temp_weight, item["quantityType"]])
    
    
    recipes, extra = find_meals(groceries)

    left_weight = 0
    for item in extra:
        if item[1] < len(recipes) // 3:
            left_weight += item[2]

    response = {}

    response["LeftProducts"] = extra
    response["Recipes"] = recipes
    response["PercentageOfWaste"] = left_weight / total_weight
    
    print([recipe["url"] for recipe in recipes])
    return ujson.dumps(response)