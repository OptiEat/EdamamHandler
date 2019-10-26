import urllib.request, ujson


app_id = "98b8c38a"
api_key = "e4b94dc003b4c7e97d8d96b66bd31e22"


def _read_json(url):
    with urllib.request.urlopen(url) as url2:
        data = ujson.loads(url2.read().decode())
        return data


def _compose_url(ingredients, extra_ingredients):
    return u"https://api.edamam.com/search?q={0}&app_id={1}&app_key={2}&ingr={3}&to=100".format(
        ",".join(ingredients),
        app_id,
        api_key,
        len(ingredients) + extra_ingredients
    )


def _is_ingredient_in_recipe(ingredient, recipe_ingredients):
    for item in recipe_ingredients:
        item = item["text"].lower()
        if ingredient in item:
            return True

def _get_weight_for_ingredient(ingredient, recipe_ingredients):
    for item in recipe_ingredients:
        text = item["text"].lower()
        if ingredient in text:
            return item["weight"]
    

def chose_recipe_from_data(data, ingredients):
    ingredients = [x.lower() for x in ingredients]
    for recipe in data["hits"]:
        recipe = recipe["recipe"]
        recipe_ingredients = recipe["ingredients"]
        if all([_is_ingredient_in_recipe(ingredient, recipe_ingredients) for ingredient in ingredients]):
            return recipe
    return None


def get_weight_for_recipe(recipe, ingredients):
    recipe_ingredients = recipe["ingredients"]
    return [[ingredient, _get_weight_for_ingredient(ingredient, recipe_ingredients)] for ingredient in ingredients]
    
            
def find_recipe(ingredients, margin):
    data = _read_json(_compose_url(ingredients, margin))
    return chose_recipe_from_data(data, ingredients)

if __name__ == "__main__":
    ingredients = ["chicken", "curry", "rice"]
    recipe = find_recipe(ingredients)
    if not recipe:
        print("Could not find the recipe")
        exit(1)
    print(get_weight_for_recipe(recipe, ingredients))
    print(recipe["url"])
    
        