import urllib.request, ujson


app_id = "98b8c38a"
api_key = "e4b94dc003b4c7e97d8d96b66bd31e22"


def _read_json(url):
    with urllib.request.urlopen(url) as url2:
        data = ujson.loads(url2.read().decode())
        return data


def _compose_url(ingredients, allowed_extra_ingredients):
    return u"https://api.edamam.com/search?q={0}&app_id={1}&app_key={2}&ingr={3}&to=100".format(
        ",".join(ingredients),
        app_id,
        api_key,
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
        ingredients_name = [x[0] for x in groceries]
        ingredients_grams = [x[2] for x in groceries]
        i = 1       
        recipe = None
        ingredients = None
        while not recipe and i < len(groceries):
            ingredients = [ingredients_name[0], ingredients_name[i]]
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
        first_ratio = ingredients_grams[0] / ingredients_usage[0]
        second_ratio = ingredients_grams[i] / ingredients_usage[1]
        if first_ratio < second_ratio:
            to_remove = ingredients_grams[0] * ingredients_usage[1] / ingredients_usage[0]
            groceries[0][2] -= ingredients_grams[0]
            groceries[i][2] -= to_remove
            recipe["effectiveGrams"] = [{ingredients_name[0]: ingredients_grams[0]}, {ingredients_name[i]: to_remove}]
        else:
            to_remove = ingredients_grams[1] * ingredients_usage[0] / ingredients_usage[1]
            groceries[i][2] -= ingredients_grams[1]
            groceries[0][2] -= to_remove
            recipe["effectiveGrams"] = [{ingredients_name[0]: to_remove}, {ingredients_name[i]: ingredients_grams[1]}]
        recipes.append(recipe)
        if groceries[i][2] <= 0:
            del groceries[i]
        if groceries[0][2] <= 0:
            del groceries[0]
    
    return recipes, groceries


if __name__ == "__main__":
    temp = [
        {"id": "BANANA", "description": "Banana", "quantity": "4", "quantityType": "Count", "expiration": "7", "shortName": "banana"},
        {"id": "TF LR WH EGG DZ", "description": "White Eggs", "quantity": "6", "quantityType": "Count", "expiration": "21", "shortName": "egg"},
        {"id": "HORIZON", "description": "Horizon Milk", "quantity": "1", "quantityType": "Gallons", "expiration": "10", "shortName": "milk"},
        {"id": "HS RSTD SEAWEED 12", "description": "Roasted Seaweed", "quantity": "1", "quantityType": "Box", "expiration": "365", "shortName": "seaweed"},
        {"id": "ORG BABY CARROTS", "description": "Organic Baby Carrots", "quantity": "4", "quantityType": "Count", "expiration": "30", "shortName": "carrot"},
        {"id": "CHINJUNG KIMCHI", "description": "Kimchi", "quantity": "1", "quantityType": "Pounds", "expiration": "90", "shortName": "kimchi"},
        {"id": "SY HOT CHICKEN RAM", "description": "Hot Chicken Ramen", "quantity": "1", "quantityType": "Box", "expiration": "365", "shortName": "ramen"},
        {"id": "RED ONION", "description": "Red Onions", "quantity": "2", "quantityType": "Count", "expiration": "35", "shortName": "onion"},
        {"id": "GRN SEEDLESS GRAPE", "description": "Seedless Grapes", "quantity": "15", "quantityType": "Ounces", "expiration": "9", "shortName": "grape"},
        {"id": "HAIO HN GRPFRT TEA", "description": "Grapefruit Tea", "quantity": "1", "quantityType": "Gallons", "expiration": "365", "shortName": "tea"},
        {"id": "KD PURE SESAME OIL", "description": "Pure Sesame Oil", "quantity": "20", "quantityType": "Fl Oz", "expiration": "180", "shortName": "oil"},
        {"id": "NS SHIN RAMYUN 4PK", "description": "Shin Ramen", "quantity": "4", "quantityType": "Packs", "expiration": "365", "shortName": "ramen"},
        {"id": "WRIGLEY", "description": "Wrigley's Gum", "quantity": "1", "quantityType": "Packs", "expiration": "3650", "shortName": "gum"},
        {"id": "SHJ WASABI GR PEAS", "description": "Wasabi Green Peas", "quantity": "20", "quantityType": "Ounces", "expiration": "7", "shortName": "pea"},
        {"id": "WHITE PEACH", "description": "White Peaches", "quantity": "2", "quantityType": "Count", "expiration": "5", "shortName": "peach"},
        {"id": "Hikari Menra Ramen", "description": "Hikari Menra Ramen", "quantity": "1", "quantityType": "Boxes", "expiration": "365", "shortName": "ramen"},
        {"id": "GKM TONKOTSU RAMEN", "description": "Tonkotsu Ramen", "quantity": "1", "quantityType": "Boxes", "expiration": "365", "shortName": "ramen"}
    ]
    
    groceries = []
    for item in temp:
        groceries.append([item["shortName"], int(item["expiration"]), int(item["quantity"]) * 30])
    
    recipes, extra = find_meals(groceries)

    print(extra)
    print([recipe["url"] for recipe in recipes])