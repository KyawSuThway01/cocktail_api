from flask import Flask, jsonify, request
import random
import requests as req

app = Flask(__name__)

# ─────────────────────────────────────────
#  TheCocktailDB Fallback Image Cache
#  Fetches a real image for any cocktail
#  that has an empty images list.
#  Results are cached in memory so we only
#  hit the external API once per cocktail.
# ─────────────────────────────────────────
_image_cache = {}

def get_fallback_image(key):
    """Return a live image URL from TheCocktailDB for cocktails with no local images."""
    if key in _image_cache:
        return _image_cache[key]

    name = key.replace("_", " ")
    url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}"
    try:
        r = req.get(url, timeout=5)
        data = r.json()
        if data.get("drinks"):
            img = data["drinks"][0].get("strDrinkThumb", "")
            _image_cache[key] = img
            return img
    except Exception:
        pass

    _image_cache[key] = None
    return None

# ─────────────────────────────────────────
#  CORS — allow all origins for frontend access
# ─────────────────────────────────────────
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,OPTIONS"
    return response

# ─────────────────────────────────────────
#  Cocktail Data (100 cocktails)
# ─────────────────────────────────────────
cocktails = {
    "bukit_highball": {
        "description": "A whisky-based Mule-style drink enriched with sweet bitterness from Dubonnet, herbs and botanicals from Benedictine, topped with Ginger Beer and a dash of citrus.",
        "ingredients": ["Whisky", "Dubonnet", "Benedictine", "Ginger Beer", "Citrus"],
        "images": ["https://citynomads.com/wp-content/uploads/2023/10/Highballs-Feature-767x628.jpg",
                   "https://1.bp.blogspot.com/-u3ds7NAHFGg/XNJVjnI9BoI/AAAAAAACgAQ/pO0x_Fj4fuAECSvT-KNBmByI_c9Qfqq-QCLcBGAs/s1600/Highball.jpg"
                   ]
    },
    "braids_boulevardier": {
        "description": "A contemporary Coffee Negroni twist with Dark Rum, a nutty essence from Disaronno, and sesame infused through a meticulous Fat Wash process.",
        "ingredients": ["Dark Rum", "Coffee", "Disaronno", "Sesame (Fat Wash)"],
        "images": ["https://ichef.bbci.co.uk/food/ic/food_16x9_1600/recipes/boulevardier_45459_16x9.jpg",
                   "https://static01.nyt.com/images/2018/01/25/dining/25COOKING-Boulevardier1/25COOKING-Boulevardier1-jumbo.jpg",
                   "https://candradrinks.com/wp-content/uploads/2022/08/Boulevardier-2-min-scaled.jpg"]
    },
    "club_maker": {
        "description": "An Old Fashioned-style elixir combining Coconut-infused Whisky and Sweet Vermouth, simmered with spices and enhanced with Homemade Chocolate Bitters.",
        "ingredients": ["Coconut-infused Whisky", "Sweet Vermouth", "Spices", "Homemade Chocolate Bitters"],
        "images": ["https://www.thebottleclub.com/cdn/shop/articles/Classic_Club_Cocktail_Recipe.jpg?v=1703659568&width=1024",
                   "https://www.wellseasonedstudio.com/wp-content/uploads/2022/05/A-clover-club-cocktail-with-raspberries.jpg"
                   "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRVXAsgbcyiUu7ddPV2h3GIIb8BP4C71iEiLA&s"
                   ]
    },
    "amaro": {
        "description": "A sweet and sour Negroni variation with a hint of vanilla and silky egg white texture, transforming a traditionally bitter cocktail into an approachable drink.",
        "ingredients": ["Gin", "Amaro", "Vanilla", "Egg White"],
        "images": ["https://theepicureantrader.com/cdn/shop/articles/top-10-amaro-cocktails-you-need-to-try-833477.jpg?v=1737431882",
                   "https://punchdrink.com/wp-content/uploads/2018/11/Slide4-Amaro-Cynar-Averna-Braulio-Cocktail-Recipe.jpg",
                   "https://www.add1tbsp.com/wp-content/uploads/2018/09/20180506-italian-amaro-cocktail-1.jpg"]
    },
    "flora": {
        "description": "A highly floral and fruity gin cocktail infused with Rose Water and Lychee, customisable between sweet or tangy, finished with a silky egg white texture.",
        "ingredients": ["Gin", "Rose Water", "Lychee or Passion Fruit", "Egg White"],
        "images": [ "https://putneyfarm.com/wp-content/uploads/2019/05/img_0316-e1558130367954.jpg",
                    "https://craftandcocktails.co/wp-content/uploads/2018/04/Flora-and-Juniper-1-of-9.jpg"
        ]
    },
    "cupid": {
        "description": "A refreshing Shrub cordial gin drink with strawberry and vinegar for revitalising acidity, topped with soda for a lively effervescence.",
        "ingredients": ["Gin", "Strawberry Shrub", "Vinegar", "Soda"],
        "images": ["https://www.finamill.com/cdn/shop/articles/cupid_kiss_b20c04d7-bb04-4a52-ad95-66c102017390.jpg?v=1745506834"]
    },
    "immortal_khaya": {
        "description": "Inspired by the 100-year-old Khaya tree, this vibrant green vodka cocktail blends sourness, sweetness, and subtle peppery undertones.",
        "ingredients": ["Vodka", "Pepper", "Honey", "Green Apple"],
        "images": ["https://www.epicureasia.com/wp-content/uploads/2024/06/X7V05586-HD-Fits.jpg"]
    },
    "albatross": {
        "description": "A milk punch clarified for a pristine appearance, with an exceptionally gentle and velvety texture derived from Cognac, Fino Sherry, and Honey.",
        "ingredients": ["Cognac", "Fino Sherry", "Vermouth", "Honey", "Milk"],
        "images": ["https://www.bcliquorstores.com/sites/default/files/recipe/BarStar_Albatross_KI.jpg"]
    },
    "the_braid_martini": {
        "description": "A timeless Dry Martini crafted from the house 1924 Gin and dry vermouth, personalised with aromatic botanical options of lavender, rose, or jasmine.",
        "ingredients": ["1924 Gin", "Dry Vermouth", "Lavender / Rose / Jasmine"],
        "images": ["https://www.cocktailicious.nl/wp-content/uploads/2019/12/Pornstar_Martini_cocktail.jpg"]
    },
    "1924": {
        "description": "The Braid Bar's signature Tiki-style cocktail, a fruity and refreshing homage to the house 1924 Gin, maintaining its full alcoholic strength.",
        "ingredients": ["1924 Gin", "Rosemary", "Orange"],
        "images": ["https://pentrubar.ro/2781-large_default/vintage-1924-cocktail-coupe-glass-libbey-245ml.jpg"]
    },
    "negroni": {
        "description": "A classic bitter Italian cocktail with equal parts gin, Campari, and sweet vermouth, balanced and aromatic.",
        "ingredients": ["Gin", "Campari", "Sweet Vermouth"],
        "images": ["https://www.liquor.com/thmb/KPTRXSVO7vyx7O2fPyNkLh9JQPo=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/mezcal-negroni-1500x1500-primary-6f6c472050a949c8a55aa07e1b5a2d1b.jpg"]
    },
    "old_fashioned": {
        "description": "A timeless whisky cocktail gently sweetened with brown sugar and balanced with aromatic bitters.",
        "ingredients": ["Whisky", "Bitters", "Brown Sugar", "Orange Peel"],
        "images": ["https://www.simplyrecipes.com/thmb/s_de1Nuw4ULiHNECVHOCBY5u5Wk=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/__opt__aboutcom__coeus__resources__content_migration__simply_recipes__uploads__2020__01__Old-Fashioned-Cocktail-LEAD-5-1024x681-aa81a798a156453d80d1f7d41de893ff.jpg"]
    },
    "manhattan": {
        "description": "A sophisticated whisky cocktail stirred with sweet vermouth and bitters, elegant and spirit-forward.",
        "ingredients": ["Whisky", "Sweet Vermouth", "Bitters"],
        "images": ["https://www.liquor.com/thmb/DR2UAsRlu-YCVn9r_iLJCmOvzlg=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/manhattan-4000x4000-primary-ig-9c3d894510284e9d8fbd9c518d00790b.jpg"]
    },
    "martini": {
        "description": "The ultimate classic cocktail — clean, cold, and elegant with gin or vodka and a whisper of dry vermouth.",
        "ingredients": ["Gin or Vodka", "Dry Vermouth"],
        "images": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQtGSduNnEAMfKdIUFp8VRJIJknw-14tKsLEA&s"]
    },
    "bloody_mary": {
        "description": "A bold and savoury classic brunch cocktail with a spicy kick from Tabasco and depth from Worcestershire sauce.",
        "ingredients": ["Vodka", "Worcestershire Sauce", "Tabasco", "Lemon Juice", "Pepper", "Tomato Juice"],
        "images": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR2iJJBpAXlbBrElkFzuu8_eFvdP-ukhUVzCQ&s"]
    },
    "pina_colada": {
        "description": "A tropical classic blending creamy coconut and sweet pineapple with rum for a lush, island-inspired refreshment.",
        "ingredients": ["Rum", "Coconut Cream", "Pineapple Juice"],
        "images": ["https://salimaskitchen.com/wp-content/uploads/2024/07/10-Minute-Pina-Colada-Recipe-A-Classic-Puerto-Rican-Cocktail-Salimas-Kitchen-4-3.jpg"]
    },
    "whisky_sour": {
        "description": "A perfectly balanced whisky cocktail with a bright citrus tang from lemon juice and a touch of sweetness.",
        "ingredients": ["Whisky", "Lemon Juice", "Sugar", "Egg White"],
        "images": ["https://www.urbanbar.com/cdn/shop/articles/Whisky_sour.jpg?v=1671203012&width=1500"]
    },
    "singapore_sling": {
        "description": "Singapore's iconic gin cocktail, fruity and tropical with Cointreau, grenadine, and pineapple juice.",
        "ingredients": ["Gin", "Cointreau", "Grenadine", "Pineapple Juice"],
        "images": ["https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSJbCKTlONdRoBStZRUY03uqeS8252FEScn0g&s"]
    },
    "long_island_iced_tea": {
        "description": "A potent party favourite combining five spirits with lime and cola for a surprisingly refreshing yet strong drink.",
        "ingredients": ["Gin", "Rum", "Vodka", "Tequila", "Cointreau", "Lime", "Coke"],
        "images": ["https://www.supergoldenbakes.com/wordpress/wp-content/uploads/2019/07/Long_island_iced_tea-1-4s.jpg"]
    },
    "cosmopolitan": {
        "description": "A chic and vibrant vodka cocktail made famous by its striking pink hue and balance of tart cranberry and citrus.",
        "ingredients": ["Vodka", "Orange Liqueur", "Cranberry Juice", "Lime Juice"],
        "images": ["https://assets.bonappetit.com/photos/650df690c94ec4218673b45a/6:9/w_1300,h_1950,c_limit/20230915-WEB-SEO-0882_update%20copy.jpg"]
    },
    "rob_roy": {
        "description": "A Scottish twist on the Manhattan using Scotch whisky, sweet vermouth, and bitters for a smooth, peaty depth.",
        "ingredients": ["Scotch Whisky", "Sweet Vermouth", "Bitters"],
        "images": ["https://www.wineenthusiast.com/wp-content/uploads/2023/06/06_23_Rob_Roy_HERO_GlenDronach_Distillery_1920x1280.jpg"]
    },
    "mary_pickford": {
        "description": "A Prohibition-era classic blending rum, cherry liqueur, and pineapple for a sweet and fruity tropical experience.",
        "ingredients": ["Rum", "Cherry Liqueur", "Pineapple Juice", "Grenadine"],
        "images": ["https://upload.wikimedia.org/wikipedia/commons/1/1a/Mary_Pickford_Cocktail.jpg"]
    },
    "sidecar": {
        "description": "A refined Cognac classic with bright citrus from orange liqueur and a sour punch from lemon juice.",
        "ingredients": ["Cognac", "Orange Liqueur", "Lemon Juice"],
        "images": ["https://upload.wikimedia.org/wikipedia/commons/9/94/Sidecar-cocktail.jpg"]
    },
    "sazerac": {
        "description": "One of the oldest known cocktails, a bold rye whisky drink with absinthe rinse and aromatic bitters.",
        "ingredients": ["Rye Whisky", "Bitters", "Absinthe", "Sugar"],
        "images": ["https://static-prod.remymartin.com/app/uploads/2024/06/remy-martin-cocktails-sazerac-1x1-250716-02.jpg"]
    },
    "martinez": {
        "description": "The forefather of the modern martini, combining gin and sweet vermouth with a hint of orange bitters.",
        "ingredients": ["Gin", "Sweet Vermouth", "Orange Bitters"],
        "images": ["https://punchdrink.com/wp-content/uploads/2013/12/Social-Martini-Cocktail-Recipe-Martinez.jpg"]
    },
    "mojito": {
        "description": "A refreshing Cuban classic bursting with fresh mint, lime, and light rum, topped with soda for effervescence.",
        "ingredients": ["White Rum", "Fresh Mint", "Lime Juice", "Sugar", "Soda Water"],
        "images": ["https://www.liquor.com/thmb/MJRVqf-itJGY90nwUOYGXnyG-HA=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/mojito-720x720-primary-6a57f80e200c412e9a77a1687f312ff7.jpg"]
    },
    "daiquiri": {
        "description": "A beautifully simple rum cocktail with a perfect balance of sweet and sour, crisp and refreshing.",
        "ingredients": ["White Rum", "Lime Juice", "Simple Syrup"],
        "images": ["https://www.liquor.com/thmb/WjUD7EuXuhZ98tfYtOjdfmuA-y4=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Strawberry_Daquiri_1800x1800_primary-63c25c677616479da2d08767b3b4ee8a.jpg"]
    },
    "margarita": {
        "description": "The world's most popular tequila cocktail, bright and tangy with a salted rim and fresh lime juice.",
        "ingredients": ["Tequila", "Triple Sec", "Lime Juice", "Salt"],
        "images": ["https://soufflebombay.com/wp-content/uploads/2017/05/Classic-Margarita-Recipe.jpg"]
    },
    "aperol_spritz": {
        "description": "A light and bittersweet Italian aperitivo, effervescent and vibrant with Aperol, prosecco, and soda.",
        "ingredients": ["Aperol", "Prosecco", "Soda Water", "Orange Slice"],
        "images": ["https://www.liquor.com/thmb/1ZharnCZtEmyUkKfEm8dh07MV8g=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/aperol-spritz-720x720-primary-985457b239d7427da2f8b4be17131caa.jpg"]
    },
    "espresso_martini": {
        "description": "A sophisticated coffee cocktail that delivers a caffeinated kick with a velvety, frothy finish.",
        "ingredients": ["Vodka", "Espresso", "Coffee Liqueur", "Simple Syrup"],
        "images": ["https://barossadistilling.com/wp-content/uploads/2024/05/Espresso-Martini-Cocktail.png"]
    },
    "tom_collins": {
        "description": "A tall, refreshing gin cocktail with lemon juice and soda water, light and effervescent for warm days.",
        "ingredients": ["Gin", "Lemon Juice", "Simple Syrup", "Soda Water"],
        "images": ["https://assets.epicurious.com/photos/642da48f6f7f88309f457815/1:1/w_4634,h_4634,c_limit/TomCollins_RECIPE_033123_50633.jpg"]
    },
    "french_75": {
        "description": "An elegant celebratory cocktail combining gin and lemon juice topped with champagne for a sparkling finish.",
        "ingredients": ["Gin", "Lemon Juice", "Simple Syrup", "Champagne"],
        "images": ["https://images.ctfassets.net/hs93c4k6gio0/Qh3XDKsj9fkaFAPbIcLXR/43bcbac62e7807e55e7a5c91b822e79b/_images_us-cocktails_French75_0412_2.jpg.jpg"]
    },
    "gimlet": {
        "description": "A clean and sharp gin cocktail with a balance of citrus and sweetness, timeless and easy to drink.",
        "ingredients": ["Gin", "Lime Juice", "Simple Syrup"],
        "images": ["https://punchdrink.com/wp-content/uploads/2013/09/Gimlet.jpg"]
    },
    "dark_and_stormy": {
        "description": "A bold and spicy highball pairing dark rum with fiery ginger beer and a squeeze of lime.",
        "ingredients": ["Dark Rum", "Ginger Beer", "Lime Juice"],
        "images": ["https://www.foodandwine.com/thmb/q-xC6FQ9lRW19WmlNmyydrPGmko=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/FAW-recipes-dark-n-stormy-hero-c4c68e82794f409fa86c6dbc14f5a350.jpg"]
    },
    "paloma": {
        "description": "Mexico's most beloved tequila cocktail, bright and tart with grapefruit soda and a salted rim.",
        "ingredients": ["Tequila", "Grapefruit Juice", "Lime Juice", "Salt", "Soda Water"],
        "images": ["https://imbibemagazine.com/wp-content/uploads/2025/07/Puesto_PoblanoPaloma-crdt-Mandie-Geller.jpg"]
    },
    "whisky_highball": {
        "description": "A simple and endlessly satisfying Japanese-style whisky drink with chilled soda water over ice.",
        "ingredients": ["Whisky", "Soda Water"],
        "images": ["https://www.liquor.com/thmb/1wYZ_FaWjTxLHBE9fadgvuTbFLM=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/whiskey-highball-1500x1500-hero-aa13a49019364fab8c94b53861aeb182.jpg"]
    },
    "clover_club": {
        "description": "A pre-Prohibition classic with a gorgeous pink hue from raspberry syrup and a silky texture from egg white.",
        "ingredients": ["Gin", "Lemon Juice", "Raspberry Syrup", "Egg White"],
        "images": ["https://www.foodandwine.com/thmb/cohxXZsvVl5sPfAZ702iNWyEY44=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Clover_Club_Cocktail_Credit_Tim_Nusog_4000x2667-e52131de178048e784ecfdd25b586daf.jpg"]
    },
    "bees_knees": {
        "description": "A Prohibition-era gin cocktail sweetened with honey and brightened with fresh lemon, smooth and aromatic.",
        "ingredients": ["Gin", "Honey Syrup", "Lemon Juice"],
        "images": ["https://www.girlversusdough.com/wp-content/uploads/2021/04/bees-knees-cocktail-3-600x900.jpg"]
    },
    "penicillin": {
        "description": "A modern classic combining blended Scotch, honey-ginger syrup, and lemon juice with a smoky Islay float.",
        "ingredients": ["Blended Scotch Whisky", "Islay Single Malt", "Honey-Ginger Syrup", "Lemon Juice"],
        "images": ["https://www.thespruceeats.com/thmb/kZ8yHPOE-rSmbsYrFYIw6caHzF8=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/SES-penicillin-cocktail-recipe-7374904-hero-01-31bce98ad0194410b3fd41c318206dad.jpg"]
    },
    "paper_plane": {
        "description": "A modern equal-parts cocktail that is simultaneously bitter, sweet, and sour with a beautiful amber hue.",
        "ingredients": ["Bourbon", "Aperol", "Amaro Nonino", "Lemon Juice"],
        "images": ["https://www.liquor.com/thmb/JHYqlZiH5R0pbhUQCIho5QTxC6Q=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/paper-plane-720x720-primary-3e0b79b1d81c4e7e8f017093d4b27f12.jpg"]
    },
    "jungle_bird": {
        "description": "A Tiki classic from Kuala Lumpur featuring the unexpected bitterness of Campari balanced with rum and tropical fruits.",
        "ingredients": ["Dark Rum", "Campari", "Pineapple Juice", "Lime Juice", "Simple Syrup"],
        "images": ["https://punchdrink.com/wp-content/uploads/2021/09/Social2-Mastering-the-Jungle-Bird-Cocktail-Recipe-Fanny-Chu.jpg"]
    },
    "amaretto_sour": {
        "description": "A sweet and tangy cocktail with the distinctive almond flavour of Amaretto, lifted by bright lemon juice and frothy egg white.",
        "ingredients": ["Amaretto", "Lemon Juice", "Simple Syrup", "Egg White"],
        "images": ["https://www.realsimple.com/thmb/Tci1QDDA5BmOUAUfGZqcvueI7ms=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/RealSimple_amaretto-sour_Step-3-16746e54b17640b5bc2c075f90fd9b1e.jpg"]
    },
    "aviation": {
        "description": "A stunning violet-hued classic gin cocktail with floral notes from creme de violette and bright maraschino cherry liqueur.",
        "ingredients": ["Gin", "Maraschino Liqueur", "Creme de Violette", "Lemon Juice"],
        "images": ["https://www.thespruceeats.com/thmb/CHRUnCNBw3TdWNVIvSK_OgJ7QJw=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/aviation-cocktail-recipe-760055-hero-01-af5233300c184476b02891de2c685b2a.jpg"]
    },
    "last_word": {
        "description": "A Prohibition-era equal-parts cocktail with herbal green Chartreuse, gin, maraschino, and lime — perfectly balanced.",
        "ingredients": ["Gin", "Green Chartreuse", "Maraschino Liqueur", "Lime Juice"],
        "images": ["https://kitchenswagger.com/wp-content/uploads/2018/09/last-word-1-1.jpg"]
    },
    "corpse_reviver_no2": {
        "description": "A classic hangover cure combining gin, lemon, Cointreau, and Lillet Blanc with a hint of absinthe.",
        "ingredients": ["Gin", "Cointreau", "Lillet Blanc", "Lemon Juice", "Absinthe"],
        "images": ["https://www.supergoldenbakes.com/wordpress/wp-content/uploads/2019/12/Corpse_Reviver_No2.jpg"]
    },
    "pornstar_martini": {
        "description": "A fruity and indulgent modern classic with vanilla vodka and passion fruit, served alongside a shot of Prosecco.",
        "ingredients": ["Vanilla Vodka", "Passion Fruit Puree", "Passion Fruit Liqueur", "Lime Juice", "Prosecco"],
        "images": ["https://punchdrink.com/wp-content/uploads/2023/06/Article-Ultimate-Porn-Star-Martini-Recpie.jpg?w=800"]
    },
    "sex_on_the_beach": {
        "description": "A fruity and fun vodka cocktail combining peach schnapps with cranberry and orange juice for a tropical vibe.",
        "ingredients": ["Vodka", "Peach Schnapps", "Cranberry Juice", "Orange Juice"],
        "images": ["https://images.immediate.co.uk/production/volatile/sites/2/2022/05/sex-on-the-beach-0026fb2.jpg"]
    },
    "tequila_sunrise": {
        "description": "A visually stunning cocktail with a gradient of orange juice and grenadine resembling a beautiful sunrise.",
        "ingredients": ["Tequila", "Orange Juice", "Grenadine"],
        "images": []
    },
    "harvey_wallbanger": {
        "description": "A groovy 1970s classic layering Galliano herbal liqueur over a simple vodka and orange juice combination.",
        "ingredients": ["Vodka", "Orange Juice", "Galliano"],
        "images": ["https://images.immediate.co.uk/production/volatile/sites/2/2022/05/tequila-sunrise-a164206.jpg"]
    },
    "bahama_mama": {
        "description": "A fruity tropical rum cocktail bursting with pineapple, coconut, and a hint of coffee liqueur.",
        "ingredients": ["Dark Rum", "Coconut Rum", "Coffee Liqueur", "Pineapple Juice", "Orange Juice", "Lime Juice"],
        "images": ["https://www.liquor.com/thmb/mQ16ZSRMMjwmxoKtwHCINvk3RmU=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/bahama-mama-720x720-primary-155c67b9c3bb41f4bac182875c904518.jpg"]
    },
    "moscow_mule": {
        "description": "A refreshing and zingy vodka cocktail served in its iconic copper mug with spicy ginger beer and lime.",
        "ingredients": ["Vodka", "Ginger Beer", "Lime Juice"],
        "images": ["https://www.liquor.com/thmb/G5R_Y6cS-voBV1hYqI2mtoovoTQ=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/moscow-mule-4000x4000-primary-ig-3a364d63e57b4a9b8cf82ec1dc54eb30.jpg"]
    },
    "mint_julep": {
        "description": "The quintessential Kentucky Derby cocktail — bourbon over crushed ice with fresh mint and a touch of sugar.",
        "ingredients": ["Bourbon", "Fresh Mint", "Simple Syrup", "Crushed Ice"],
        "images": ["https://www.liquor.com/thmb/EJQYiAb0wheEgC5VfuoTph3mTkw=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/__opt__aboutcom__coeus__resources__content_migration__liquor__2019__09__03134428__Miamians-Julep-720x720-recipe-fb97ac8873054d3487ecb2bbb26e94be.jpg"]
    },
    "french_connection": {
        "description": "A simple yet indulgent after-dinner drink combining Cognac and Amaretto in a smooth, nutty pairing.",
        "ingredients": ["Cognac", "Amaretto"],
        "images": ["https://ik.imagekit.io/vjt1kualr/drinks/french_connection/main-image.jpg"]
    },
    "stinger": {
        "description": "A classic digestif pairing smooth Cognac with refreshing white crème de menthe for a cooling finish.",
        "ingredients": ["Cognac", "White Creme de Menthe"],
        "images": []
    },
    "rusty_nail": {
        "description": "A warming Scottish duo of Scotch whisky and Drambuie, honeyed and herbal with a smooth lingering finish.",
        "ingredients": ["Scotch Whisky", "Drambuie"],
        "images": []
    },
    "godfather": {
        "description": "A bold and nutty two-ingredient Scotch cocktail softened by the sweet almond notes of Disaronno Amaretto.",
        "ingredients": ["Scotch Whisky", "Amaretto"],
        "images": []
    },
    "black_russian": {
        "description": "A simple and strong Soviet-inspired cocktail pairing vodka with rich coffee liqueur over ice.",
        "ingredients": ["Vodka", "Coffee Liqueur"],
        "images": []
    },
    "white_russian": {
        "description": "A creamy, indulgent twist on the Black Russian made famous by The Big Lebowski, topped with heavy cream.",
        "ingredients": ["Vodka", "Coffee Liqueur", "Heavy Cream"],
        "images": []
    },
    "grasshopper": {
        "description": "A sweet and minty dessert cocktail with a vibrant green colour from creme de menthe and creamy texture.",
        "ingredients": ["Green Creme de Menthe", "White Creme de Cacao", "Heavy Cream"],
        "images": []
    },
    "hurricane": {
        "description": "A bold New Orleans Tiki classic loaded with passion fruit, citrus, and two kinds of rum for tropical indulgence.",
        "ingredients": ["Dark Rum", "White Rum", "Passion Fruit Syrup", "Orange Juice", "Lime Juice", "Grenadine"],
        "images": []
    },
    "zombie": {
        "description": "A legendary and dangerously strong Tiki cocktail blending three types of rum with tropical fruits and spice.",
        "ingredients": ["White Rum", "Dark Rum", "Overproof Rum", "Apricot Brandy", "Pineapple Juice", "Lime Juice", "Grenadine"],
        "images": []
    },
    "mai_tai": {
        "description": "The king of Tiki cocktails — a rum-forward blend of orange liqueur, orgeat, and lime with an exotic tropical flair.",
        "ingredients": ["White Rum", "Dark Rum", "Orange Liqueur", "Orgeat Syrup", "Lime Juice"],
        "images": []
    },
    "blue_hawaii": {
        "description": "A vibrant electric-blue Tiki cocktail with vodka, rum, blue curacao, and tropical pineapple juice.",
        "ingredients": ["Vodka", "White Rum", "Blue Curacao", "Pineapple Juice", "Sweet and Sour Mix"],
        "images": []
    },
    "lemon_drop": {
        "description": "A bright and citrusy vodka martini with a sugar-rimmed glass and a sharp lemon punch.",
        "ingredients": ["Vodka", "Triple Sec", "Lemon Juice", "Simple Syrup", "Sugar"],
        "images": []
    },
    "kamikaze": {
        "description": "A sharp and tangy vodka shooter with triple sec and lime, clean and easy to throw back.",
        "ingredients": ["Vodka", "Triple Sec", "Lime Juice"],
        "images": []
    },
    "between_the_sheets": {
        "description": "A cheeky Prohibition-era cocktail blending rum, Cognac, and Cointreau with bright lemon for a balanced sip.",
        "ingredients": ["White Rum", "Cognac", "Cointreau", "Lemon Juice"],
        "images": []
    },
    "bramble": {
        "description": "A modern British classic by Dick Bradsell — gin sour drizzled with blackberry liqueur for a fruity forest finish.",
        "ingredients": ["Gin", "Lemon Juice", "Simple Syrup", "Creme de Mure"],
        "images": []
    },
    "southside": {
        "description": "A refreshing Prohibition-era gin cocktail similar to a mojito, with bright mint and citrus notes.",
        "ingredients": ["Gin", "Fresh Mint", "Lime Juice", "Simple Syrup"],
        "images": []
    },
    "naked_and_famous": {
        "description": "A bold and equal-parts modern classic balancing smoky mezcal with Aperol, yellow Chartreuse, and lime.",
        "ingredients": ["Mezcal", "Aperol", "Yellow Chartreuse", "Lime Juice"],
        "images": []
    },
    "mezcal_negroni": {
        "description": "A smoky and complex twist on the classic Negroni swapping gin for earthy mezcal for added depth.",
        "ingredients": ["Mezcal", "Campari", "Sweet Vermouth"],
        "images": []
    },
    "tommy_s_margarita": {
        "description": "A purist tequila-forward Margarita using agave nectar instead of triple sec to let the tequila shine.",
        "ingredients": ["Tequila", "Lime Juice", "Agave Nectar"],
        "images": []
    },
    "spicy_margarita": {
        "description": "A fiery twist on the classic Margarita with fresh jalapeño and chilli-infused tequila for a bold kick.",
        "ingredients": ["Tequila", "Triple Sec", "Lime Juice", "Jalapeño", "Salt"],
        "images": []
    },
    "frozen_daiquiri": {
        "description": "A slushy and refreshing blended version of the classic daiquiri, perfect for hot tropical days.",
        "ingredients": ["White Rum", "Lime Juice", "Simple Syrup", "Crushed Ice"],
        "images": []
    },
    "strawberry_daiquiri": {
        "description": "A fruity and sweet blended cocktail with fresh strawberries, rum, and lime for a summery treat.",
        "ingredients": ["White Rum", "Fresh Strawberries", "Lime Juice", "Simple Syrup"],
        "images": []
    },
    "mango_margarita": {
        "description": "A tropical twist on the classic Margarita bursting with fresh mango sweetness and zesty lime.",
        "ingredients": ["Tequila", "Mango Puree", "Triple Sec", "Lime Juice"],
        "images": []
    },
    "cucumber_gin_fizz": {
        "description": "A light and crisp gin cocktail with fresh cucumber and elderflower topped with soda for garden-party freshness.",
        "ingredients": ["Gin", "Cucumber", "Elderflower Liqueur", "Lime Juice", "Soda Water"],
        "images": []
    },
    "elderflower_collins": {
        "description": "A delicate and floral twist on the Tom Collins with elderflower liqueur adding a fragrant sweetness.",
        "ingredients": ["Gin", "Elderflower Liqueur", "Lemon Juice", "Soda Water"],
        "images": []
    },
    "blood_orange_margarita": {
        "description": "A stunning ruby-red Margarita with the rich, slightly tart flavour of freshly squeezed blood orange juice.",
        "ingredients": ["Tequila", "Blood Orange Juice", "Triple Sec", "Lime Juice"],
        "images": []
    },
    "pisco_sour": {
        "description": "Peru's national cocktail — a frothy, citrusy sour made with pisco brandy and finished with aromatic bitters.",
        "ingredients": ["Pisco", "Lime Juice", "Simple Syrup", "Egg White", "Bitters"],
        "images": []
    },
    "caipirinha": {
        "description": "Brazil's national cocktail — muddled lime and sugar with earthy cachaça for a raw, refreshing punch.",
        "ingredients": ["Cachaça", "Lime", "Sugar"],
        "images": []
    },
    "irish_coffee": {
        "description": "A warming classic combining hot Irish whiskey and coffee, topped with a thick layer of lightly whipped cream.",
        "ingredients": ["Irish Whiskey", "Hot Coffee", "Brown Sugar", "Heavy Cream"],
        "images": []
    },
    "spanish_coffee": {
        "description": "A flambéed coffee cocktail layering rum, Kahlua, and Triple Sec under hot coffee and whipped cream.",
        "ingredients": ["Rum", "Kahlua", "Triple Sec", "Hot Coffee", "Whipped Cream"],
        "images": []
    },
    "black_velvet": {
        "description": "An elegant and luxurious drink layering creamy Guinness stout over chilled sparkling wine or Champagne.",
        "ingredients": ["Guinness Stout", "Champagne or Sparkling Wine"],
        "images": []
    },
    "kir_royale": {
        "description": "A simple and elegant French aperitif of Champagne with a splash of blackcurrant creme de cassis.",
        "ingredients": ["Champagne", "Creme de Cassis"],
        "images": []
    },
    "bellini": {
        "description": "A classic Italian brunch cocktail from Venice combining white peach puree with light and bubbly Prosecco.",
        "ingredients": ["Prosecco", "White Peach Puree"],
        "images": []
    },
    "mimosa": {
        "description": "A brunch icon blending chilled Champagne with fresh orange juice in a beautifully simple 50/50 ratio.",
        "ingredients": ["Champagne", "Orange Juice"],
        "images": []
    },
    "death_in_the_afternoon": {
        "description": "An Ernest Hemingway creation combining absinthe with Champagne for a dangerously smooth and elegant sip.",
        "ingredients": ["Absinthe", "Champagne"],
        "images": []
    },
    "tipperary": {
        "description": "A rich and herbal pre-Prohibition Irish cocktail combining Irish whiskey, sweet vermouth, and green Chartreuse.",
        "ingredients": ["Irish Whiskey", "Sweet Vermouth", "Green Chartreuse"],
        "images": ["https://mybartender.com/wp-content/uploads/2023/12/tipperary-cocktail-recipe.jpg"]
    },
    "vieux_carre": {
        "description": "A New Orleans classic blending rye whiskey, Cognac, sweet vermouth, Benedictine, and bitters in equal harmony.",
        "ingredients": ["Rye Whiskey", "Cognac", "Sweet Vermouth", "Benedictine", "Peychaud Bitters", "Angostura Bitters"],
        "images": ["https://drinkinghobby.com/wp-content/uploads/2018/06/Vieux-Carre-cocktail-28-Blog.jpg"]
    },
    "toronto": {
        "description": "A spirit-forward Canadian cocktail featuring rye whisky sweetened and deepened with Fernet-Branca amaro.",
        "ingredients": ["Rye Whisky", "Fernet-Branca", "Simple Syrup", "Angostura Bitters"],
        "images": ["https://punchdrink.com/wp-content/uploads/2023/01/Social-Toronto-Cocktail-Recipe-Jamie-Bourdreau-Canon-Seattle.jpg"]
    },
    "trinidad_sour": {
        "description": "A daring modern cocktail built on a full ounce of Angostura bitters, balanced with orgeat and lemon juice.",
        "ingredients": ["Angostura Bitters", "Orgeat Syrup", "Lemon Juice", "Rye Whisky"],
        "images": ["https://www.foodandwine.com/thmb/QFqSackTjNKMoe5AMKCBNJ9cpuY=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/trinidad-sour-FT-RECIPE1025-272d97e433be4d0c8665c07ad937f3eb.jpg"]
    },
    "final_ward": {
        "description": "A modern riff on the Last Word swapping gin for rye whiskey for a spicier, more complex equal-parts cocktail.",
        "ingredients": ["Rye Whiskey", "Green Chartreuse", "Maraschino Liqueur", "Lemon Juice"],
        "images": ["https://bar-vademecum.eu/wp-content/uploads/2021/04/Final-Ward-1.jpg"]
    },
    "revolver": {
        "description": "A bold coffee-forward Bourbon cocktail with Kahlua and orange bitters for a rich, warming nightcap.",
        "ingredients": ["Bourbon", "Kahlua", "Orange Bitters"],
        "images": ["https://www.liquor.com/thmb/YO9-iwg4pbDlxNE64JeZ0_ZWar8=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/__opt__aboutcom__coeus__resources__content_migration__liquor__2019__04__24153243__revolver-720x720-recipe-1-f662b26f4c3e49588c629a4533c8830b.jpg"]
    },
    "oaxacan_old_fashioned": {
        "description": "A celebrated modern classic combining mezcal and reposado tequila for a smoky, complex Old Fashioned.",
        "ingredients": ["Reposado Tequila", "Mezcal", "Agave Nectar", "Mole Bitters"],
        "images": ["https://www.slightlypretentious.co/wp-content/uploads/2021/12/Oaxacan-Old-Fashioned-2-1024x683.jpg"]
    },
    "shirley_temple": {
        "description": "A classic non-alcoholic mocktail for all ages with ginger ale and grenadine for a sweet, fizzy sip.",
        "ingredients": ["Ginger Ale", "Grenadine", "Orange Juice"],
        "images": ["https://vintageamericancocktails.com/wp-content/uploads/2023/01/shirley_temple-1.jpg"]
    },
    "blue_lagoon_mocktail": {
        "description": "A vivid blue non-alcoholic cooler with blue curacao syrup, lemon juice, and lemonade for a tropical feel.",
        "ingredients": ["Blue Curacao Syrup", "Lemon Juice", "Lemonade", "Soda Water"],
        "images": ["https://frobishers.com/cdn/shop/articles/blue_lagoon_3.png?v=1695025795"]
    },
    "cucumber_mint_cooler": {
        "description": "A light and refreshing non-alcoholic mocktail with fresh cucumber, mint, and a hint of lime.",
        "ingredients": ["Cucumber", "Fresh Mint", "Lime Juice", "Soda Water", "Simple Syrup"],
        "images": ["https://empirewine.imgix.net/recipes/203_1723664773009.jpg?w=1200"]
    },
    "jungle_juice": {
        "description": "A potent party punch combining multiple spirits with tropical juices for a crowd-pleasing, fruit-forward drink.",
        "ingredients": ["Vodka", "Rum", "Fruit Punch", "Orange Juice", "Pineapple Juice", "Lemon-Lime Soda"],
        "images": ["https://vintageamericancocktails.com/wp-content/uploads/2020/11/jungle-juice.jpg"]
    },
    "sex_and_the_city": {
        "description": "A glamorous and fruity vodka cocktail inspired by the iconic TV series, bursting with citrus and berry flavours.",
        "ingredients": ["Vodka", "Raspberry Liqueur", "Cranberry Juice", "Lime Juice"],
        "images": []
    },
    "absinthe_drip": {
        "description": "A traditional French preparation of absinthe with ice-cold water dripped slowly over a sugar cube to louche the spirit.",
        "ingredients": ["Absinthe", "Ice Water", "Sugar Cube"],
        "images": ["https://drinksworld.com/wp-content/uploads/Absinthe-Drip-Ingredients-scaled.jpg"]
    },
    "remember_the_maine": {
        "description": "A complex and smoky Manhattan variation with Cherry Heering and absinthe for a dramatic depth of flavour.",
        "ingredients": ["Rye Whisky", "Sweet Vermouth", "Cherry Heering", "Absinthe"],
        "images": ["https://australianbartender.com.au/wp-content/uploads/2018/06/remember_the_maine_DSC9517.jpg"]
    },
    "cafe_caribbean": {
        "description": "A tropical coffee concoction blending Caribbean rum with rich coffee for a warm and indulgent after-dinner treat.",
        "ingredients": ["Caribbean Rum", "Hot Coffee", "Sugar", "Whipped Cream"],
        "images": ["https://www.thespruceeats.com/thmb/m9i2cJPy1kM9by2c5j8-dZ45RAk=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/cafe-caribbean-cocktail-recipe-760506-hero-images-3-dcd499a7c0cf44e491a76e04598a97d5.jpg"]
    }
}




# ─────────────────────────────────────────
#  Cocktail History Data (10 iconic cocktails)
# ─────────────────────────────────────────
cocktail_history = {
    "old_fashioned": {
        "name": "Old Fashioned",
        "year": "1806",
        "origin": "United States",
        "era": "19th Century",
        "summary": "The Old Fashioned is widely considered the original cocktail. The word 'cocktail' was first defined in 1806 as a mix of spirits, sugar, water, and bitters — which is exactly what an Old Fashioned is. By the 1880s, bartenders began adding unnecessary garnishes and liqueurs, prompting patrons to request their drink made the 'old fashioned' way. The name stuck. It remains one of the most ordered cocktails in the world.",
        "fun_fact": "President Franklin D. Roosevelt reportedly celebrated the end of Prohibition in 1933 by mixing Old Fashioneds for his staff.",
        "image": "https://www.liquor.com/thmb/oatRTuOoMojsHW4-KydgBYh4uT4=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/old-fashioned-720x720-primary-6628052faee04b3a95f975b5ff1e2388.jpg"
    },
    "martini": {
        "name": "Martini",
        "year": "1880s",
        "origin": "United States",
        "era": "Gilded Age",
        "summary": "The Martini's exact origin is disputed — some trace it to Martinez, California in the 1860s, while others credit New York bartenders in the 1880s. Originally made with sweet vermouth and gin, it evolved into the drier version we know today. By the 1920s it became the defining drink of sophistication. Ernest Hemingway, Winston Churchill, and Dorothy Parker all had famously strong opinions about the perfect Martini ratio.",
        "fun_fact": "Winston Churchill's preferred method was to simply glance at a bottle of vermouth across the room while drinking his gin — he liked his Martini bone dry.",
        "image": "https://www.liquor.com/thmb/oSRqGIJFhTAMKgUmHIKJj4S7JNQ=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/dry-martini-720x720-primary-6628052faee04b3a95f975b5ff1e2388.jpg"
    },
    "negroni": {
        "name": "Negroni",
        "year": "1919",
        "origin": "Florence, Italy",
        "era": "Post-WWI",
        "summary": "The Negroni was born in Florence, Italy in 1919 when Count Camillo Negroni asked bartender Fosco Scarselli to strengthen his Americano by replacing soda water with gin. The bartender also switched the orange slice for an orange peel to signify it was a different drink. The Count's family later opened the Negroni distillery to produce a ready-made version of the cocktail, cementing its place in history.",
        "fun_fact": "The Negroni is one of the few cocktails named after a real person who actually invented it — most cocktail origin stories are disputed myths.",
        "image": "https://www.liquor.com/thmb/KPTRXSVO7vyx7O2fPyNkLh9JQPo=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/mezcal-negroni-1500x1500-primary-6f6c472050a949c8a55aa07e1b5a2d1b.jpg"
    },
    "manhattan": {
        "name": "Manhattan",
        "year": "1874",
        "origin": "New York City, USA",
        "era": "Gilded Age",
        "summary": "The Manhattan is said to have been created at the Manhattan Club in New York City around 1874, allegedly for a banquet hosted by Lady Randolph Churchill — mother of Winston Churchill. However historians note she was likely in England at the time, pregnant. The true origin remains debated, but what is certain is that by the 1880s the Manhattan was already one of the most popular cocktails in America, setting the template for all stirred, spirit-forward cocktails.",
        "fun_fact": "The Manhattan is believed to be the first cocktail to use vermouth as a key ingredient, sparking the entire vermouth cocktail category.",
        "image": "https://www.liquor.com/thmb/DR2UAsRlu-YCVn9r_iLJCmOvzlg=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/manhattan-4000x4000-primary-ig-9c3d894510284e9d8fbd9c518d00790b.jpg"
    },
    "mojito": {
        "name": "Mojito",
        "year": "1500s",
        "origin": "Havana, Cuba",
        "era": "Colonial Era",
        "summary": "The Mojito traces its roots to 16th century Cuba. Sir Francis Drake's crew used a primitive version called 'El Draque' — made with aguardiente, mint, lime, and sugar — to combat scurvy and dysentery. As Cuban rum improved in quality, aguardiente was replaced, and the modern Mojito was born. It became internationally famous when Ernest Hemingway adopted it as his drink of choice at La Bodeguita del Medio bar in Havana during the 1940s and 50s.",
        "fun_fact": "Ernest Hemingway wrote on the wall of La Bodeguita del Medio: 'My mojito in La Bodeguita, my daiquiri in El Floridita' — though some historians believe this was a marketing invention.",
        "image": "https://www.liquor.com/thmb/MJRVqf-itJGY90nwUOYGXnyG-HA=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/mojito-720x720-primary-6a57f80e200c412e9a77a1687f312ff7.jpg"
    },
    "daiquiri": {
        "name": "Daiquiri",
        "year": "1898",
        "origin": "Daiquiri, Cuba",
        "era": "Spanish-American War Era",
        "summary": "The Daiquiri was invented by American mining engineer Jennings Cox near the town of Daiquiri, Cuba in 1898. Running low on gin to serve guests, Cox mixed local rum with lime juice and sugar — and the Daiquiri was born. Naval officer Lucius Johnson brought the recipe to the Army and Navy Club in Washington D.C., spreading it across the United States. During WWII, whisky and other spirits were rationed, making rum-based Daiquiris enormously popular.",
        "fun_fact": "JFK was such a fan of Daiquiris that the drink reportedly became fashionable among Washington's political elite during his presidency.",
        "image": "https://www.liquor.com/thmb/WjUD7EuXuhZ98tfYtOjdfmuA-y4=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/Strawberry_Daquiri_1800x1800_primary-63c25c677616479da2d08767b3b4ee8a.jpg"
    },
    "margarita": {
        "name": "Margarita",
        "year": "1938",
        "origin": "Mexico / USA Border",
        "era": "Prohibition Aftermath",
        "summary": "The Margarita has at least seven disputed origin stories. The most widely accepted credits socialite Margarita Sames who created it at her Acapulco villa in 1948. Others credit Dallas restaurant owner Santos Cruz who made it for singer Peggy Lee in 1948, or bartender Danny Herrera who created it for actress Marjorie King in 1938. Regardless of origin, by the 1950s it was appearing in magazines, and by the 1970s it had become America's most ordered cocktail.",
        "fun_fact": "The frozen Margarita machine was invented by Dallas restaurateur Mariano Martinez in 1971, inspired by a 7-Eleven Slurpee machine.",
        "image": "https://soufflebombay.com/wp-content/uploads/2017/05/Classic-Margarita-Recipe.jpg"
    },
    "singapore_sling": {
        "name": "Singapore Sling",
        "year": "1915",
        "origin": "Singapore",
        "era": "Colonial Era",
        "summary": "The Singapore Sling was created around 1915 by bartender Ngiam Tong Boon at the Long Bar of Raffles Hotel in Singapore. At the time, it was considered improper for women to drink alcohol in public, so Ngiam crafted a cocktail that resembled fruit punch — allowing women to drink discreetly. The pink, fruity drink was a social revolution in its time. The original recipe was lost and rediscovered in the 1970s from a scribbled note found in the hotel's safe.",
        "fun_fact": "Raffles Hotel still serves over 1,000 Singapore Slings per day, making it one of the most consistently ordered cocktails at a single venue in the world.",
        "image": "https://www.liquor.com/thmb/aHEFMpnbDpnKxDjrqU9aVmKbPUE=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/singapore-sling-720x720-primary-6628052faee04b3a95f975b5ff1e2388.jpg"
    },
    "sazerac": {
        "name": "Sazerac",
        "year": "1838",
        "origin": "New Orleans, USA",
        "era": "Antebellum America",
        "summary": "The Sazerac is often called America's first cocktail. It was created in New Orleans around 1838 by Antoine Amedie Peychaud, a Creole apothecary who served brandy toddies with his own bitters in an egg cup called a 'coquetier' — which Americans mispronounced as 'cocktay', possibly giving us the word 'cocktail'. The drink evolved to use rye whisky after a phylloxera epidemic wiped out European cognac production in the 1870s. New Orleans declared it the city's official cocktail in 2008.",
        "fun_fact": "The Sazerac may have inadvertently given us the word 'cocktail' — Peychaud's egg cup coquetier allegedly became the mispronounced origin of the term.",
        "image": "https://static-prod.remymartin.com/app/uploads/2024/06/remy-martin-cocktails-sazerac-1x1-250716-02.jpg"
    },
    "mai_tai": {
        "name": "Mai Tai",
        "year": "1944",
        "origin": "Oakland, California, USA",
        "era": "Post-WWII Tiki Era",
        "summary": "The Mai Tai was invented in 1944 by Trader Vic (Victor Bergeron) at his restaurant in Oakland, California. He shook up the drink for two friends visiting from Tahiti — Ham and Carrie Guild. Upon tasting it, Carrie reportedly exclaimed 'Mai Tai — Roa Ae!' meaning 'Out of this world — the best!' in Tahitian, and the drink had its name. The Mai Tai became the signature drink of the entire Tiki cocktail movement that swept America in the post-WWII era.",
        "fun_fact": "Donn Beach (Don the Beachcomber) claimed he invented the Mai Tai earlier, sparking a lifelong rivalry with Trader Vic that was never officially resolved.",
        "image": "https://www.liquor.com/thmb/e3f9o53cCHVbFbPzN4k5M5iZhOM=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/mai-tai-720x720-primary-f518d5df5e9c4e2da5b9de4d4b4b4e78.jpg"
    }
}


# ─────────────────────────────────────────
#  Food Pairing Data (25 dishes)
# ─────────────────────────────────────────
food_pairings = {
    "wagyu_beef": {
        "name": "Wagyu Beef",
        "category": "Meat",
        "description": "Exceptionally marbled Japanese beef with an intensely buttery, umami-rich flavour and a melt-in-the-mouth texture. The high fat content calls for cocktails that cut through richness while complementing its depth.",
        "flavour_profile": ["Rich", "Buttery", "Umami", "Savoury"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2024/04/Wagyu-Steak_6.jpg",
        "pairings": [
            {
                "cocktail": "Old Fashioned",
                "cocktail_id": "old_fashioned",
                "reason": "Bourbon's caramel and vanilla notes mirror the beef's richness, while the bitters cut through the fat and cleanse the palate between bites.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Manhattan",
                "cocktail_id": "manhattan",
                "reason": "Rye whisky's spice and sweet vermouth's herbal complexity complement wagyu's deep umami without overpowering it.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Whisky Highball",
                "cocktail_id": "whisky_highball",
                "reason": "The effervescence cleanses the palate of rich fat between bites — a classic Japanese pairing tradition.",
                "match_level": "Excellent"
            }
        ]
    },
    "sashimi": {
        "name": "Sashimi",
        "category": "Seafood",
        "description": "Thinly sliced raw fish of the highest quality — typically salmon, tuna, or yellowtail. Clean, delicate, and oceanic with a silky texture that demands equally clean, refreshing cocktails.",
        "flavour_profile": ["Clean", "Delicate", "Oceanic", "Umami"],
        "image": "https://www.justonecookbook.com/wp-content/uploads/2022/08/Sashimi-0070-I.jpg",
        "pairings": [
            {
                "cocktail": "Martini",
                "cocktail_id": "martini",
                "reason": "The dry, clean botanicals of gin mirror the purity of fresh fish, while cold temperature and salinity echo the oceanic flavour.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "Lime's brightness lifts the delicate fat of raw fish, creating a refreshing contrast that highlights the sashimi's subtle sweetness.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Whisky Highball",
                "cocktail_id": "whisky_highball",
                "reason": "A traditional Japanese pairing — the light effervescence and gentle whisky notes complement raw fish without masking its flavour.",
                "match_level": "Excellent"
            }
        ]
    },
    "tom_yum": {
        "name": "Tom Yum",
        "category": "Soup",
        "description": "Thailand's iconic hot and sour soup, fragrant with lemongrass, kaffir lime, galangal, and chilli. Bold, aromatic, and intensely spiced — it calls for cocktails that cool and refresh.",
        "flavour_profile": ["Spicy", "Sour", "Aromatic", "Herbal"],
        "image": "https://hot-thai-kitchen.com/wp-content/uploads/2022/01/Tom-yum-goong-sq.jpg",
        "pairings": [
            {
                "cocktail": "Mojito",
                "cocktail_id": "mojito",
                "reason": "Fresh mint and lime echo the herbaceous lemongrass and citrus in the soup, while the coolness tames the chilli heat.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Moscow Mule",
                "cocktail_id": "moscow_mule",
                "reason": "Ginger beer's spice harmonises with galangal's warmth, while lime and effervescence cut through the soup's bold aromatics.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "The sharp citrus-forward profile refreshes the palate between spoonfuls of the intensely flavoured broth.",
                "match_level": "Good"
            }
        ]
    },
    "truffle_pasta": {
        "name": "Truffle Pasta",
        "category": "Pasta",
        "description": "Fresh pasta enveloped in a luxurious truffle cream sauce — earthy, deeply aromatic, and indulgently rich. The pungent umami of black truffle demands cocktails with complexity and structure.",
        "flavour_profile": ["Earthy", "Rich", "Aromatic", "Creamy"],
        "image": "https://www.sipandfeast.com/wp-content/uploads/2022/09/truffle-pasta-recipe-snippet.jpg",
        "pairings": [
            {
                "cocktail": "Negroni",
                "cocktail_id": "negroni",
                "reason": "The bitter botanicals of the Negroni cut through the cream's richness, while the sweet vermouth mirrors the earthy depth of truffles.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Manhattan",
                "cocktail_id": "manhattan",
                "reason": "The rye spice and vermouth complexity echo truffle's layered earthiness, creating an elegant high-low contrast.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Old Fashioned",
                "cocktail_id": "old_fashioned",
                "reason": "Bourbon's vanilla and oak notes harmonise beautifully with truffle's pungent, forest-floor aroma.",
                "match_level": "Excellent"
            }
        ]
    },
    "grilled_octopus": {
        "name": "Grilled Octopus",
        "category": "Seafood",
        "description": "Charred, tender octopus with smoky caramelised edges and a clean oceanic sweetness, typically served with citrus, herbs, or a Mediterranean salsa verde.",
        "flavour_profile": ["Smoky", "Oceanic", "Charred", "Tender"],
        "image": "https://www.themediterraneandish.com/wp-content/uploads/2020/07/grilled-octopus-recipe-3.jpg",
        "pairings": [
            {
                "cocktail": "Aperol Spritz",
                "cocktail_id": "aperol_spritz",
                "reason": "The bittersweet orange notes of Aperol and the effervescence complement the smoky char and oceanic sweetness of the octopus.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Paloma",
                "cocktail_id": "paloma",
                "reason": "Grapefruit's tartness cuts through the charred smokiness while complementing the seafood's natural salinity.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "Crisp lime and gin botanicals echo Mediterranean herbs, cleansing the smoky aftertaste.",
                "match_level": "Good"
            }
        ]
    },
    "beef_tartare": {
        "name": "Beef Tartare",
        "category": "Meat",
        "description": "Raw, hand-chopped premium beef seasoned with capers, shallots, Dijon mustard, and egg yolk. Bold, briny, and intensely savoury — a dish that commands equally bold cocktails.",
        "flavour_profile": ["Briny", "Savoury", "Bold", "Rich"],
        "image": "https://www.foodandwine.com/thmb/6-XXsGBGRxFrFKUXUGMGQI5O7Bc=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/classic-steak-tartare-FT-RECIPE0321-dad2692a3f6b45f8b6f38c6b72a11a22.jpg",
        "pairings": [
            {
                "cocktail": "Martini",
                "cocktail_id": "martini",
                "reason": "The clean, cold clarity of a dry Martini echoes the tartare's precise seasoning — both are exercises in elegant restraint.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Sazerac",
                "cocktail_id": "sazerac",
                "reason": "The absinthe rinse and rye spice provide a bold counterpoint to the rich raw beef and briny capers.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Bloody Mary",
                "cocktail_id": "bloody_mary",
                "reason": "The tomato, horseradish, and Worcestershire create a savoury mirror to the tartare's briny umami profile.",
                "match_level": "Excellent"
            }
        ]
    },
    "lobster_bisque": {
        "name": "Lobster Bisque",
        "category": "Soup",
        "description": "A velvety, cream-enriched shellfish soup with deep oceanic sweetness, a hint of brandy, and aromatic tarragon. Rich and luxurious — it needs cocktails with enough presence to stand alongside it.",
        "flavour_profile": ["Sweet", "Creamy", "Oceanic", "Luxurious"],
        "image": "https://www.spendwithpennies.com/wp-content/uploads/2022/01/Lobster-Bisque-SpendWithPennies-2.jpg",
        "pairings": [
            {
                "cocktail": "French 75",
                "cocktail_id": "french_75",
                "reason": "The Champagne and lemon lift the bisque's heavy cream richness, while the gin botanicals complement the lobster's sweetness.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Sidecar",
                "cocktail_id": "sidecar",
                "reason": "Cognac shares the bisque's brandy base, while the orange liqueur and citrus brighten the dish's creamy sweetness.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Aperol Spritz",
                "cocktail_id": "aperol_spritz",
                "reason": "The light bitterness and effervescence cut through the cream and refresh the palate between spoonfuls.",
                "match_level": "Good"
            }
        ]
    },
    "foie_gras": {
        "name": "Foie Gras",
        "category": "Delicacy",
        "description": "Silky pan-seared duck liver with an extraordinary buttery richness and subtle sweetness, typically served with brioche and fruit compote. One of the world's most indulgent dishes.",
        "flavour_profile": ["Buttery", "Rich", "Sweet", "Silky"],
        "image": "https://www.finedininglovers.com/sites/g/files/xknfdk626/files/styles/article_1200_800_fallback/public/2021-11/foie-gras%401200x800.jpg",
        "pairings": [
            {
                "cocktail": "Sidecar",
                "cocktail_id": "sidecar",
                "reason": "Cognac's stone fruit richness matches foie gras's luxurious fat, while the citrus provides essential acidity to balance the richness.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "French 75",
                "cocktail_id": "french_75",
                "reason": "Champagne's bubbles and acidity cut through the fat with elegance — the classic French pairing for a classic French delicacy.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Vieux Carré",
                "cocktail_id": "vieux_carre",
                "reason": "The Cognac and Benedictine base mirrors the French tradition behind foie gras, adding herbal complexity to the fat.",
                "match_level": "Excellent"
            }
        ]
    },
    "spicy_tuna_roll": {
        "name": "Spicy Tuna Roll",
        "category": "Sushi",
        "description": "Fresh tuna mixed with sriracha and sesame oil, rolled in seasoned rice and nori. A balance of oceanic tuna sweetness with a slow-building chilli heat and nutty sesame finish.",
        "flavour_profile": ["Spicy", "Oceanic", "Nutty", "Fresh"],
        "image": "https://www.justonecookbook.com/wp-content/uploads/2021/08/Spicy-Tuna-Roll-9018-I.jpg",
        "pairings": [
            {
                "cocktail": "Paloma",
                "cocktail_id": "paloma",
                "reason": "Grapefruit's tartness cuts the sriracha heat while complementing the tuna's oceanic sweetness and the sesame's nuttiness.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "Bright lime and clean gin provide a refreshing cooldown after the chilli heat builds.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Cucumber Gin Fizz",
                "cocktail_id": "cucumber_gin_fizz",
                "reason": "Cool cucumber and elderflower soothe the spice while echoing the clean, fresh flavours of the roll.",
                "match_level": "Excellent"
            }
        ]
    },
    "lamb_chops": {
        "name": "Lamb Chops",
        "category": "Meat",
        "description": "Herb-crusted rack of lamb with a rosemary and garlic crust, perfectly pink in the centre. Gamey, rich, and aromatic — a dish that pairs beautifully with bold, complex cocktails.",
        "flavour_profile": ["Gamey", "Herbal", "Rich", "Aromatic"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2020/12/Lamb-chops_1.jpg",
        "pairings": [
            {
                "cocktail": "Rob Roy",
                "cocktail_id": "rob_roy",
                "reason": "Scotch whisky's peaty earthiness and herbal vermouth mirror the lamb's gamey richness and rosemary crust.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Negroni",
                "cocktail_id": "negroni",
                "reason": "Campari's bitter herbal notes contrast the richness of lamb fat beautifully, while the gin botanicals echo the herb crust.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Manhattan",
                "cocktail_id": "manhattan",
                "reason": "The sweet vermouth and whisky structure complement the gamey depth of lamb without overpowering it.",
                "match_level": "Good"
            }
        ]
    },
    "oysters": {
        "name": "Oysters",
        "category": "Seafood",
        "description": "Fresh raw oysters served on ice with mignonette and lemon — briny, mineral, and oceanic with an incredibly clean finish. One of the most cocktail-friendly foods in existence.",
        "flavour_profile": ["Briny", "Mineral", "Oceanic", "Clean"],
        "image": "https://www.seriouseats.com/thmb/Z_mHIFe7h7J9mMaX4K5Q5t9X4gA=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/20211117-oysters-on-halfshell-vicky-wasik-seriouseats-1-735f42de66874f3d9ad2c0dc1faae600.jpg",
        "pairings": [
            {
                "cocktail": "Martini",
                "cocktail_id": "martini",
                "reason": "The definitive oyster pairing. The saline, mineral quality of a cold dry Martini is a direct mirror of the oyster's oceanic brine.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "French 75",
                "cocktail_id": "french_75",
                "reason": "Champagne's minerality and fine bubbles echo the oyster's ocean brine — a classic French tradition of pairing the two.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Corpse Reviver No. 2",
                "cocktail_id": "corpse_reviver_no2",
                "reason": "The absinthe rinse and Lillet Blanc bring herbal anise notes that pair classically with raw shellfish.",
                "match_level": "Excellent"
            }
        ]
    },
    "duck_confit": {
        "name": "Duck Confit",
        "category": "Meat",
        "description": "Duck leg slow-cooked in its own fat until the skin is shatteringly crisp and the meat is fall-off-the-bone tender. Rich, deeply savoury, and intensely flavoured.",
        "flavour_profile": ["Rich", "Crispy", "Savoury", "Deep"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2021/08/Duck-Confit_6.jpg",
        "pairings": [
            {
                "cocktail": "Vieux Carré",
                "cocktail_id": "vieux_carre",
                "reason": "The New Orleans classic with Cognac and Benedictine mirrors duck confit's French origins while the rye spice cuts the fat.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Rob Roy",
                "cocktail_id": "rob_roy",
                "reason": "Scotch whisky's smokiness and the herbal vermouth complement the richness of duck fat and crispy skin.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Sazerac",
                "cocktail_id": "sazerac",
                "reason": "The absinthe complexity and rye spice cut through duck's intense richness, cleansing the palate between bites.",
                "match_level": "Excellent"
            }
        ]
    },
    "tiramisu": {
        "name": "Tiramisu",
        "category": "Dessert",
        "description": "Italy's iconic layered dessert of espresso-soaked ladyfingers and mascarpone cream, dusted with cocoa. Coffee-forward, gently sweet, and indulgently creamy.",
        "flavour_profile": ["Coffee", "Sweet", "Creamy", "Cocoa"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2021/11/Tiramisu_1.jpg",
        "pairings": [
            {
                "cocktail": "Espresso Martini",
                "cocktail_id": "espresso_martini",
                "reason": "A natural marriage — the espresso and coffee liqueur in the cocktail directly mirror the dessert's core flavour, amplifying the coffee experience.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "White Russian",
                "cocktail_id": "white_russian",
                "reason": "Coffee liqueur and cream echo tiramisu's mascarpone and espresso in liquid form — essentially the same flavour profile.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Stinger",
                "cocktail_id": "stinger",
                "reason": "The menthol freshness of crème de menthe provides a refreshing contrast to the dense cocoa and cream.",
                "match_level": "Good"
            }
        ]
    },
    "caesar_salad": {
        "name": "Caesar Salad",
        "category": "Salad",
        "description": "Crisp romaine lettuce dressed in an anchovy-rich, garlicky, lemony Caesar dressing with shaved Parmesan and house-made croutons. Bold umami with bright acidity.",
        "flavour_profile": ["Umami", "Tangy", "Savoury", "Crisp"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2016/08/Caesar-Salad_9.jpg",
        "pairings": [
            {
                "cocktail": "Bloody Mary",
                "cocktail_id": "bloody_mary",
                "reason": "The savoury, umami-rich Bloody Mary mirrors the Caesar's anchovy and Worcestershire backbone — both are bold, savoury classics.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Tom Collins",
                "cocktail_id": "tom_collins",
                "reason": "The light, lemony effervescence echoes the salad's citrus dressing and refreshes the palate between bites.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "Lime's brightness complements the tangy Caesar dressing while gin's botanicals echo the herbal Parmesan notes.",
                "match_level": "Good"
            }
        ]
    },
    "chocolate_lava_cake": {
        "name": "Chocolate Lava Cake",
        "category": "Dessert",
        "description": "Warm dark chocolate fondant with a molten liquid centre that flows when cut — intense, bittersweet, and luxuriously rich. One of the world's most indulgent desserts.",
        "flavour_profile": ["Bittersweet", "Intense", "Rich", "Warm"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2020/01/Chocolate-Lava-Cake_5.jpg",
        "pairings": [
            {
                "cocktail": "Oaxacan Old Fashioned",
                "cocktail_id": "oaxacan_old_fashioned",
                "reason": "Mezcal's smoke and the mole bitters create a dark, complex pairing that mirrors the bittersweet chocolate's depth.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Espresso Martini",
                "cocktail_id": "espresso_martini",
                "reason": "Coffee's bitterness amplifies dark chocolate's complexity, while the vodka base keeps it clean and sharp.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Revolver",
                "cocktail_id": "revolver",
                "reason": "The coffee-forward bourbon and Kahlua pair directly with the dark chocolate — warm, sweet, and deeply satisfying.",
                "match_level": "Excellent"
            }
        ]
    },
    "pad_thai": {
        "name": "Pad Thai",
        "category": "Noodles",
        "description": "Thailand's beloved stir-fried rice noodles with tamarind, fish sauce, eggs, bean sprouts, and peanuts. Sweet, sour, salty, and savoury in perfect balance with a subtle wok smokiness.",
        "flavour_profile": ["Sweet", "Sour", "Salty", "Nutty"],
        "image": "https://hot-thai-kitchen.com/wp-content/uploads/2015/02/pad-thai-new-sq.jpg",
        "pairings": [
            {
                "cocktail": "Singapore Sling",
                "cocktail_id": "singapore_sling",
                "reason": "The tropical fruit sweetness and pineapple juice harmonise with tamarind's sweet-sour profile and peanut's richness.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Mojito",
                "cocktail_id": "mojito",
                "reason": "Mint and lime provide a refreshing, clean contrast to the wok smokiness and fish sauce saltiness.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Paloma",
                "cocktail_id": "paloma",
                "reason": "Grapefruit's bitterness cuts through the noodle dish's richness while the salt rim echoes the dish's seasoning.",
                "match_level": "Good"
            }
        ]
    },
    "burrata": {
        "name": "Burrata",
        "category": "Cheese",
        "description": "Fresh Italian mozzarella filled with stracciatella and cream — extraordinarily milky, soft, and rich. Typically served with heirloom tomatoes, basil, and a drizzle of olive oil.",
        "flavour_profile": ["Milky", "Fresh", "Creamy", "Delicate"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2022/06/Burrata_5.jpg",
        "pairings": [
            {
                "cocktail": "Aperol Spritz",
                "cocktail_id": "aperol_spritz",
                "reason": "Italy's favourite aperitivo pairs with Italy's favourite starter — the bittersweet orange notes complement the tomato acidity and olive oil.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Flora",
                "cocktail_id": "flora",
                "reason": "The floral, delicate gin profile and rose water echo burrata's milky freshness and the basil's herbal notes.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "French 75",
                "cocktail_id": "french_75",
                "reason": "Champagne's acidity and fine bubbles cut the cream's richness elegantly — a light, celebratory pairing.",
                "match_level": "Good"
            }
        ]
    },
    "peking_duck": {
        "name": "Peking Duck",
        "category": "Meat",
        "description": "Ceremonial Chinese roasted duck with lacquered, mahogany-crisp skin, served with thin pancakes, hoisin sauce, cucumber, and spring onion. Sweet, smoky, and intensely savoury.",
        "flavour_profile": ["Smoky", "Sweet", "Crispy", "Savoury"],
        "image": "https://omnivorescookbook.com/wp-content/uploads/2022/11/221101_Peking-Duck_01.jpg",
        "pairings": [
            {
                "cocktail": "Oaxacan Old Fashioned",
                "cocktail_id": "oaxacan_old_fashioned",
                "reason": "Mezcal's smoke mirrors the duck's lacquered skin, while agave nectar echoes the hoisin sweetness.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Whisky Highball",
                "cocktail_id": "whisky_highball",
                "reason": "A classic East Asian pairing — the light effervescence and mellow whisky wash the palate of the rich duck fat and sweet hoisin.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Dark and Stormy",
                "cocktail_id": "dark_and_stormy",
                "reason": "Dark rum's molasses depth and ginger beer's spice complement the duck's sweet, smoky glaze.",
                "match_level": "Good"
            }
        ]
    },
    "cheese_board": {
        "name": "Cheese Board",
        "category": "Cheese",
        "description": "A curated selection of artisan cheeses — typically spanning soft brie, aged cheddar, blue cheese, and hard manchego — served with crackers, honey, and fruit.",
        "flavour_profile": ["Varied", "Rich", "Funky", "Complex"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2020/12/Cheese-Board_5.jpg",
        "pairings": [
            {
                "cocktail": "Last Word",
                "cocktail_id": "last_word",
                "reason": "Green Chartreuse's herbal complexity creates a versatile cocktail that finds harmony with every cheese on the board.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Tipperary",
                "cocktail_id": "tipperary",
                "reason": "Irish whiskey and Chartreuse's herbal depth pair particularly well with aged hard cheeses and pungent blues.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Negroni",
                "cocktail_id": "negroni",
                "reason": "The bitter-sweet-herbal structure of a Negroni is a classic aperitivo pairing for cheese — bitterness cuts through fat and salt.",
                "match_level": "Excellent"
            }
        ]
    },
    "ceviche": {
        "name": "Ceviche",
        "category": "Seafood",
        "description": "Fresh raw fish cured in citrus juice — intensely bright, acidic, and fresh with a slight heat from ají amarillo chilli. A Peruvian icon that is clean, vibrant, and punchy.",
        "flavour_profile": ["Acidic", "Bright", "Spicy", "Fresh"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2021/03/Ceviche_5.jpg",
        "pairings": [
            {
                "cocktail": "Pisco Sour",
                "cocktail_id": "pisco_sour",
                "reason": "The national cocktail of Peru meets the national dish — citrus, pisco, and bitters mirror ceviche's acidity and complexity perfectly.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Paloma",
                "cocktail_id": "paloma",
                "reason": "Grapefruit's sharp citrus amplifies the leche de tigre and cuts through the raw fish with refreshing acidity.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Daiquiri",
                "cocktail_id": "daiquiri",
                "reason": "The lime and rum combination echoes ceviche's citrus cure while the sweetness balances the chilli heat.",
                "match_level": "Excellent"
            }
        ]
    },
    "grilled_salmon": {
        "name": "Grilled Salmon",
        "category": "Seafood",
        "description": "Salmon fillet with crispy charred skin and a moist, flaky interior — rich in omega oils with a gentle smokiness from the grill and a subtle oceanic sweetness.",
        "flavour_profile": ["Smoky", "Rich", "Oceanic", "Flaky"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2021/06/Grilled-Salmon_4.jpg",
        "pairings": [
            {
                "cocktail": "Elderflower Collins",
                "cocktail_id": "elderflower_collins",
                "reason": "Elderflower's delicate floral sweetness complements the salmon's richness, while lemon and soda cleanse the oiliness.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Cucumber Gin Fizz",
                "cocktail_id": "cucumber_gin_fizz",
                "reason": "Cool cucumber and gin botanicals provide a fresh, clean contrast to the smoky, fatty salmon.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "Sharp lime and clean gin cut through the rich omega oils and complement the charred grill flavour.",
                "match_level": "Good"
            }
        ]
    },
    "mushroom_risotto": {
        "name": "Mushroom Risotto",
        "category": "Rice",
        "description": "Slow-stirred Arborio rice with porcini and cremini mushrooms in a rich parmesan-enriched stock. Deeply earthy, umami-laden, and luxuriously creamy with a gentle nuttiness.",
        "flavour_profile": ["Earthy", "Umami", "Creamy", "Nutty"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2018/10/Mushroom-Risotto_5.jpg",
        "pairings": [
            {
                "cocktail": "Toronto",
                "cocktail_id": "toronto",
                "reason": "Fernet-Branca's herbal and earthy bitterness directly complements the porcini's deep forest-floor umami.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Negroni",
                "cocktail_id": "negroni",
                "reason": "The Negroni's bitter botanical structure cuts through the creamy risotto while sweet vermouth echoes the mushroom's earthiness.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Manhattan",
                "cocktail_id": "manhattan",
                "reason": "Rye whisky's spice and the herbal vermouth create an earthy, warming complement to the mushroom's deep umami.",
                "match_level": "Good"
            }
        ]
    },
    "tacos_al_pastor": {
        "name": "Tacos Al Pastor",
        "category": "Street Food",
        "description": "Marinated pork cooked on a vertical spit, served in soft corn tortillas with pineapple, cilantro, and onion. Smoky, sweet, citrusy, and boldly spiced.",
        "flavour_profile": ["Smoky", "Sweet", "Spicy", "Citrusy"],
        "image": "https://www.isabeleats.com/wp-content/uploads/2020/01/tacos-al-pastor-small-3.jpg",
        "pairings": [
            {
                "cocktail": "Margarita",
                "cocktail_id": "margarita",
                "reason": "The definitive Mexican pairing — tequila's agave spirit mirrors the al pastor marinade, and the salted rim echoes the taco's seasoning.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Paloma",
                "cocktail_id": "paloma",
                "reason": "Grapefruit's tartness cuts the pork's richness and fat while complementing the pineapple's tropical sweetness.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Spicy Margarita",
                "cocktail_id": "spicy_margarita",
                "reason": "Jalapeño heat doubles down on the al pastor's chilli spice — for those who love turning up the heat.",
                "match_level": "Excellent"
            }
        ]
    },
    "bruschetta": {
        "name": "Bruschetta",
        "category": "Appetiser",
        "description": "Grilled sourdough rubbed with garlic and topped with fresh heirloom tomatoes, basil, olive oil, and sea salt. Simple, bright, and intensely flavourful — quintessential Italian summer eating.",
        "flavour_profile": ["Fresh", "Bright", "Herbal", "Garlicky"],
        "image": "https://www.recipetineats.com/wp-content/uploads/2020/07/Bruschetta_5.jpg",
        "pairings": [
            {
                "cocktail": "Aperol Spritz",
                "cocktail_id": "aperol_spritz",
                "reason": "Italy's favourite aperitivo pairs with Italy's favourite starter — bittersweet orange notes complement the tomato acidity and olive oil.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Tom Collins",
                "cocktail_id": "tom_collins",
                "reason": "The lemon and soda effervescence mirrors the bruschetta's bright acidity and refreshes between bites of garlic toast.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Cupid",
                "cocktail_id": "cupid",
                "reason": "The strawberry shrub's sweet acidity and vinegar base harmonise with the tomato's brightness and olive oil's richness.",
                "match_level": "Good"
            }
        ]
    },
    "mango_sticky_rice": {
        "name": "Mango Sticky Rice",
        "category": "Dessert",
        "description": "Thai dessert of sweet glutinous rice cooked in coconut milk, served warm with fresh ripe mango and a drizzle of coconut cream. Sweet, tropical, and fragrant with pandan.",
        "flavour_profile": ["Sweet", "Tropical", "Coconut", "Fragrant"],
        "image": "https://hot-thai-kitchen.com/wp-content/uploads/2015/04/mango-sticky-rice-sq.jpg",
        "pairings": [
            {
                "cocktail": "Pina Colada",
                "cocktail_id": "pina_colada",
                "reason": "Coconut and pineapple echo the dish's coconut cream and tropical mango, creating a seamless tropical experience.",
                "match_level": "Perfect"
            },
            {
                "cocktail": "Mango Margarita",
                "cocktail_id": "mango_margarita",
                "reason": "Fresh mango doubled in cocktail form — the tequila's agave sweetness and lime cut the coconut richness.",
                "match_level": "Excellent"
            },
            {
                "cocktail": "Mai Tai",
                "cocktail_id": "mai_tai",
                "reason": "The Tiki classic's tropical rum and orgeat create a synergy with the coconut sticky rice's sweet, exotic profile.",
                "match_level": "Excellent"
            }
        ]
    }
}


# ─────────────────────────────────────────
#  Mocktails & Zero-Proof Data (20 drinks)
# ─────────────────────────────────────────
mocktails = {
    "virgin_mojito": {
        "description": "A refreshing alcohol-free take on the Cuban classic — muddled fresh mint, lime juice, and sugar topped with sparkling water for a lively, cooling effervescence.",
        "ingredients": ["Fresh Mint", "Lime Juice", "Simple Syrup", "Soda Water", "Crushed Ice"],
        "images": ["https://www.recipetineats.com/wp-content/uploads/2021/07/Virgin-Mojito_4.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Minty", "Citrusy", "Refreshing", "Light"]
    },
    "virgin_mary": {
        "description": "The bold, savoury alcohol-free version of the Bloody Mary — tomato juice with Worcestershire, Tabasco, lemon, and a celery salt rim. Every bit as punchy as the original.",
        "ingredients": ["Tomato Juice", "Worcestershire Sauce", "Tabasco", "Lemon Juice", "Celery Salt", "Pepper", "Horseradish"],
        "images": ["https://www.recipetineats.com/wp-content/uploads/2021/09/Virgin-Mary_4.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Savoury", "Spicy", "Tangy", "Bold"]
    },
    "nojito": {
        "description": "A sophisticated zero-proof Negroni alternative — bitter botanical shrub, non-alcoholic aperitivo, and a hint of citrus peel. The full Negroni complexity without any alcohol.",
        "ingredients": ["Non-Alcoholic Aperitivo", "Bitter Botanical Shrub", "Orange Peel", "Soda Water"],
        "images": ["https://www.thecocktailacademy.com/wp-content/uploads/2022/03/nojito-mocktail.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Bitter", "Herbal", "Complex", "Aromatic"]
    },
    "sparkling_elderflower_lemonade": {
        "description": "A delicate and floral zero-proof drink blending elderflower cordial with fresh lemon juice and sparkling water — light, fragrant, and perfect for warm evenings.",
        "ingredients": ["Elderflower Cordial", "Lemon Juice", "Sparkling Water", "Fresh Mint", "Cucumber Slice"],
        "images": ["https://www.recipetineats.com/wp-content/uploads/2021/06/Elderflower-Lemonade_4.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Floral", "Citrusy", "Delicate", "Refreshing"]
    },
    "watermelon_mint_cooler": {
        "description": "Freshly blended watermelon juice shaken with mint, lime, and a pinch of sea salt — vibrantly pink, naturally sweet, and incredibly refreshing.",
        "ingredients": ["Fresh Watermelon Juice", "Fresh Mint", "Lime Juice", "Sea Salt", "Soda Water"],
        "images": ["https://www.recipetineats.com/wp-content/uploads/2022/01/Watermelon-Juice_4.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Sweet", "Fruity", "Minty", "Vibrant"]
    },
    "ginger_lemon_fizz": {
        "description": "Freshly pressed ginger juice combined with honey, lemon, and topped with ginger beer — spicy, zingy, and deeply warming with a natural effervescence.",
        "ingredients": ["Fresh Ginger Juice", "Lemon Juice", "Honey Syrup", "Ginger Beer", "Lemon Slice"],
        "images": ["https://www.recipetineats.com/wp-content/uploads/2022/08/Ginger-Lemonade_4.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Spicy", "Zingy", "Sweet", "Warming"]
    },
    "hibiscus_spritz": {
        "description": "A stunning ruby-red zero-proof spritz made from hibiscus flower tea, fresh orange juice, and sparkling water — tart, floral, and visually dramatic.",
        "ingredients": ["Hibiscus Tea", "Orange Juice", "Honey Syrup", "Sparkling Water", "Orange Slice"],
        "images": ["https://www.loveandlemons.com/wp-content/uploads/2021/07/hibiscus-drink.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Tart", "Floral", "Fruity", "Vibrant"]
    },
    "virgin_pina_colada": {
        "description": "Creamy, tropical, and utterly indulgent — blended coconut cream and fresh pineapple juice served over ice. All the sunshine of the Caribbean, zero alcohol.",
        "ingredients": ["Pineapple Juice", "Coconut Cream", "Lime Juice", "Crushed Ice"],
        "images": ["https://www.recipetineats.com/wp-content/uploads/2021/07/Virgin-Pina-Colada_4.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Tropical", "Creamy", "Sweet", "Rich"]
    },
    "passionfruit_cooler": {
        "description": "Fresh passion fruit pulp shaken with lime, vanilla syrup, and topped with soda — exotic, tangy, and beautifully balanced between sweet and sour.",
        "ingredients": ["Passion Fruit Pulp", "Lime Juice", "Vanilla Syrup", "Soda Water", "Mint Sprig"],
        "images": ["https://www.recipetineats.com/wp-content/uploads/2022/04/Passionfruit-Drink_4.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Exotic", "Tangy", "Sweet", "Tropical"]
    },
    "cucumber_basil_smash": {
        "description": "Muddled cucumber and fresh basil shaken with lemon juice and honey, topped with sparkling water — clean, herbal, and incredibly sophisticated for a zero-proof drink.",
        "ingredients": ["Fresh Cucumber", "Fresh Basil", "Lemon Juice", "Honey Syrup", "Sparkling Water"],
        "images": ["https://www.loveandlemons.com/wp-content/uploads/2020/07/cucumber-basil-smash.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Herbal", "Clean", "Refreshing", "Sophisticated"]
    },
    "mango_chilli_limeade": {
        "description": "Fresh mango purée blended with lime juice and a rim of chilli salt — sweet tropical mango with a fiery kick that builds slowly on the finish.",
        "ingredients": ["Mango Puree", "Lime Juice", "Chilli Salt", "Simple Syrup", "Soda Water"],
        "images": ["https://www.isabeleats.com/wp-content/uploads/2021/07/mango-agua-fresca-small-3.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Spicy", "Tropical", "Sour", "Bold"]
    },
    "rose_lychee_fizz": {
        "description": "A delicate and feminine zero-proof cocktail — lychee juice and rose water shaken with lemon and served with sparkling water for a luxurious, floral finish.",
        "ingredients": ["Lychee Juice", "Rose Water", "Lemon Juice", "Simple Syrup", "Sparkling Water"],
        "images": ["https://www.loveandlemons.com/wp-content/uploads/2021/05/lychee-mocktail.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Floral", "Sweet", "Delicate", "Exotic"]
    },
    "spiced_apple_cider": {
        "description": "Warm or chilled spiced apple cider simmered with cinnamon, star anise, and cloves — deeply aromatic, comforting, and the perfect zero-proof autumn drink.",
        "ingredients": ["Apple Cider", "Cinnamon Stick", "Star Anise", "Cloves", "Orange Peel", "Honey"],
        "images": ["https://www.recipetineats.com/wp-content/uploads/2021/10/Mulled-Cider_4.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Spiced", "Warm", "Sweet", "Aromatic"]
    },
    "blue_lagoon_zero": {
        "description": "A vivid electric-blue zero-proof cooler with blue curacao syrup, lemon juice, and lemonade — visually stunning and refreshingly tropical.",
        "ingredients": ["Blue Curacao Syrup", "Lemon Juice", "Lemonade", "Soda Water"],
        "images": ["https://frobishers.com/cdn/shop/articles/blue_lagoon_3.png?v=1695025795"],
        "zero_proof": True,
        "flavour_profile": ["Tropical", "Sweet", "Citrusy", "Vibrant"]
    },
    "pineapple_turmeric_fizz": {
        "description": "A health-forward zero-proof cocktail blending fresh pineapple juice with turmeric, ginger, and black pepper — golden, anti-inflammatory, and surprisingly complex.",
        "ingredients": ["Pineapple Juice", "Fresh Turmeric", "Fresh Ginger", "Black Pepper", "Honey", "Sparkling Water"],
        "images": ["https://www.loveandlemons.com/wp-content/uploads/2021/03/turmeric-drink.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Earthy", "Tropical", "Spiced", "Bright"]
    },
    "virgin_cosmopolitan": {
        "description": "The glamorous zero-proof version of the iconic cosmo — cranberry juice, fresh lime, orange juice, and a hint of grenadine for that signature pink blush.",
        "ingredients": ["Cranberry Juice", "Lime Juice", "Orange Juice", "Grenadine", "Orange Peel"],
        "images": ["https://www.recipetineats.com/wp-content/uploads/2021/08/Virgin-Cosmopolitan_4.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Tart", "Fruity", "Bright", "Elegant"]
    },
    "cucumber_mint_cooler": {
        "description": "A light and refreshing zero-proof mocktail with fresh cucumber, mint, and a hint of lime — clean, cool, and effortlessly sophisticated.",
        "ingredients": ["Cucumber", "Fresh Mint", "Lime Juice", "Soda Water", "Simple Syrup"],
        "images": ["https://empirewine.imgix.net/recipes/203_1723664773009.jpg?w=1200"],
        "zero_proof": True,
        "flavour_profile": ["Cool", "Herbal", "Light", "Clean"]
    },
    "coconut_lime_refresher": {
        "description": "Chilled coconut water with fresh lime juice, a touch of agave, and a pinch of sea salt — hydrating, subtly sweet, and perfectly balanced with a tropical finish.",
        "ingredients": ["Coconut Water", "Lime Juice", "Agave Nectar", "Sea Salt", "Lime Wheel"],
        "images": ["https://www.loveandlemons.com/wp-content/uploads/2020/06/coconut-water-drink.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Tropical", "Light", "Refreshing", "Balanced"]
    },
    "strawberry_basil_lemonade": {
        "description": "Freshly muddled strawberries and basil shaken with lemon juice and honey syrup — vibrant red, sweetly aromatic, and full of summer energy.",
        "ingredients": ["Fresh Strawberries", "Fresh Basil", "Lemon Juice", "Honey Syrup", "Soda Water"],
        "images": ["https://www.recipetineats.com/wp-content/uploads/2021/07/Strawberry-Lemonade_4.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Sweet", "Herbal", "Fruity", "Bright"]
    },
    "virgin_dark_and_stormy": {
        "description": "All the drama of the original — spicy ginger beer poured over a float of dark molasses syrup with fresh lime and a pinch of sea salt. Bold and stormy without the rum.",
        "ingredients": ["Ginger Beer", "Molasses Syrup", "Lime Juice", "Sea Salt", "Lime Wedge"],
        "images": ["https://www.recipetineats.com/wp-content/uploads/2022/03/Mocktail_4.jpg"],
        "zero_proof": True,
        "flavour_profile": ["Spicy", "Bold", "Dark", "Zingy"]
    }
}


# ─────────────────────────────────────────
#  Cocktail Videos (38 videos)
#
#  HOW TO USE:
#  Store your .mp4 files in a static folder
#  or upload to a CDN/cloud storage.
#  Update VIDEO_BASE_URL to your actual URL.
#
#  Local dev:   http://localhost:5000/static/videos/
#  Render CDN:  https://your-app.onrender.com/static/videos/
#  Cloud (R2/S3/Cloudinary): your CDN URL
# ─────────────────────────────────────────
VIDEO_BASE_URL = "/static/videos/"   # ← change this to your CDN/hosting URL

cocktail_videos = {
    # ── Classic Cocktails ──────────────────
    "espresso_martini": {
        "title": "Espresso Martini",
        "filename": "espresso_martini.mp4",
        "category": "Classic",
        "description": "A step-by-step guide to the perfect espresso martini — shaken hard for that iconic frothy crema on top.",
        "cocktail_id": "espresso_martini",
        "tags": ["Coffee", "Vodka", "Shaken", "Date Night"],
        "difficulty": "Easy"
    },
    "aperol_spritz": {
        "title": "Aperol Spritz",
        "filename": "aperol_spritz.mp4",
        "category": "Classic",
        "description": "The ultimate Italian aperitivo — a vibrant orange spritz that is the definition of effortless elegance.",
        "cocktail_id": "aperol_spritz",
        "tags": ["Aperol", "Prosecco", "Spritz", "Aperitivo"],
        "difficulty": "Easy"
    },
    "margarita": {
        "title": "Margarita",
        "filename": "margarita.mp4",
        "category": "Classic",
        "description": "The world's favourite tequila cocktail — shaken with fresh lime and triple sec, served with a perfectly salted rim.",
        "cocktail_id": "margarita",
        "tags": ["Tequila", "Lime", "Shaken", "Mexican"],
        "difficulty": "Easy"
    },
    "daiquiri": {
        "title": "Daiquiri",
        "filename": "daiquiri.mp4",
        "category": "Classic",
        "description": "Three ingredients, shaken perfectly — rum, lime, and sugar. The Daiquiri is the ultimate test of a bartender's technique.",
        "cocktail_id": "daiquiri",
        "tags": ["Rum", "Lime", "Shaken", "Simple"],
        "difficulty": "Easy"
    },
    "mojito": {
        "title": "Mojito",
        "filename": "mojito.mp4",
        "category": "Classic",
        "description": "Cuba's most iconic export — fresh mint muddled with lime and sugar, topped with rum and soda. Pure refreshment.",
        "cocktail_id": "mojito",
        "tags": ["Rum", "Mint", "Muddled", "Refreshing"],
        "difficulty": "Easy"
    },
    "cosmopolitan": {
        "title": "Cosmopolitan",
        "filename": "cosmopolitan.mp4",
        "category": "Classic",
        "description": "The chic pink cocktail that defined an era — vodka, cranberry, triple sec, and lime shaken to a gorgeous blush.",
        "cocktail_id": "cosmopolitan",
        "tags": ["Vodka", "Cranberry", "Shaken", "Elegant"],
        "difficulty": "Easy"
    },
    "long_island_iced_tea": {
        "title": "Long Island Iced Tea",
        "filename": "long_island_iced_tea.mp4",
        "category": "Classic",
        "description": "Five spirits, one legendary cocktail. Built tall over ice with cola — it looks like iced tea and hits like a freight train.",
        "cocktail_id": "long_island_iced_tea",
        "tags": ["Multi-Spirit", "Built", "Party", "Strong"],
        "difficulty": "Medium"
    },
    "bloody_mary": {
        "title": "Bloody Mary",
        "filename": "bloody_mary.mp4",
        "category": "Classic",
        "description": "The ultimate brunch cocktail — rich tomato, Worcestershire, Tabasco, and vodka with a dramatic garnish.",
        "cocktail_id": "bloody_mary",
        "tags": ["Vodka", "Tomato", "Brunch", "Savoury"],
        "difficulty": "Medium"
    },
    "pina_colada": {
        "title": "Piña Colada",
        "filename": "pina_colada.mp4",
        "category": "Classic",
        "description": "Blended coconut cream and pineapple with rum — the tropical classic that tastes like a holiday in a glass.",
        "cocktail_id": "pina_colada",
        "tags": ["Rum", "Coconut", "Blended", "Tropical"],
        "difficulty": "Easy"
    },
    "martini": {
        "title": "Martini",
        "filename": "martini.mp4",
        "category": "Classic",
        "description": "The king of cocktails — cold, clean, and perfectly stirred. The Martini separates the great bartenders from the good ones.",
        "cocktail_id": "martini",
        "tags": ["Gin", "Stirred", "Elegant", "Classic"],
        "difficulty": "Medium"
    },
    "old_fashioned": {
        "title": "Old Fashioned",
        "filename": "old_fashioned.mp4",
        "category": "Classic",
        "description": "The original cocktail — whisky, sugar, and bitters stirred over one large ice cube. Timeless, bold, and perfect.",
        "cocktail_id": "old_fashioned",
        "tags": ["Whisky", "Stirred", "Bitters", "Classic"],
        "difficulty": "Easy"
    },
    "negroni": {
        "title": "Negroni",
        "filename": "negroni.mp4",
        "category": "Classic",
        "description": "Equal parts gin, Campari, and sweet vermouth — stirred until ice cold and garnished with an orange peel.",
        "cocktail_id": "negroni",
        "tags": ["Gin", "Campari", "Stirred", "Bitter"],
        "difficulty": "Easy"
    },
    # ── Whisky & Spirit-Forward ────────────
    "revolver": {
        "title": "Revolver",
        "filename": "revolver.mp4",
        "category": "Whisky",
        "description": "A bold, coffee-forward Bourbon cocktail with Kahlua and orange bitters — stirred smooth for a rich, warming nightcap.",
        "cocktail_id": "revolver",
        "tags": ["Bourbon", "Coffee", "Stirred", "Nightcap"],
        "difficulty": "Easy"
    },
    "godfather": {
        "title": "Godfather",
        "filename": "godfather.mp4",
        "category": "Whisky",
        "description": "Scotch whisky softened with Disaronno Amaretto — two ingredients, served over ice. An offer you cannot refuse.",
        "cocktail_id": "godfather",
        "tags": ["Scotch", "Amaretto", "Built", "Strong"],
        "difficulty": "Easy"
    },
    "smoked_old_fashioned": {
        "title": "Smoked Old Fashioned",
        "filename": "smoked_old_fashioned.mp4",
        "category": "Whisky",
        "description": "The classic Old Fashioned elevated — a dramatic smoke dome fills the glass before the cocktail is poured. Spectacular showmanship.",
        "cocktail_id": "old_fashioned",
        "tags": ["Whisky", "Smoked", "Theatrical", "Stirred"],
        "difficulty": "Advanced"
    },
    "next_level_old_fashioned": {
        "title": "Next Level Old Fashioned",
        "filename": "next_level_old_fashioned.mp4",
        "category": "Whisky",
        "description": "An elevated take on the classic — featuring barrel-aged bitters, hand-cut ice, and an orange oil spray for a modern twist.",
        "cocktail_id": "old_fashioned",
        "tags": ["Whisky", "Advanced", "Stirred", "Elevated"],
        "difficulty": "Advanced"
    },
    # ── Signature & Creative ───────────────
    "irish_buck": {
        "title": "Irish Buck",
        "filename": "irish_buck.mp4",
        "category": "Signature",
        "description": "Irish whiskey with ginger beer and a squeeze of lime — a smooth, warming highball that is dangerously easy to drink.",
        "cocktail_id": None,
        "tags": ["Irish Whiskey", "Ginger Beer", "Highball", "Easy Drinking"],
        "difficulty": "Easy"
    },
    "gold_rush": {
        "title": "Gold Rush",
        "filename": "gold_rush.mp4",
        "category": "Signature",
        "description": "Bourbon, honey syrup, and fresh lemon — a beautifully simple modern classic that balances sweet, sour, and spirit.",
        "cocktail_id": None,
        "tags": ["Bourbon", "Honey", "Shaken", "Citrus"],
        "difficulty": "Easy"
    },
    "hot_boys_summer": {
        "title": "Hot Boys Summer",
        "filename": "hot_boys_summer.mp4",
        "category": "Signature",
        "description": "A bold, spicy summer cocktail — infused chilli tequila with mango and lime for a drink that is hot in every sense of the word.",
        "cocktail_id": None,
        "tags": ["Tequila", "Spicy", "Mango", "Summer"],
        "difficulty": "Medium"
    },
    "solo_tu_y_yo": {
        "title": "Solo Tú y Yo",
        "filename": "solo_tu_y_yo.mp4",
        "category": "Signature",
        "description": "A romantic Spanish-inspired cocktail — floral and citrusy with a lingering finish that translates as 'just you and me'.",
        "cocktail_id": None,
        "tags": ["Floral", "Citrus", "Romantic", "Elegant"],
        "difficulty": "Medium"
    },
    "simple_cocktail": {
        "title": "Simple Cocktail",
        "filename": "simple_cocktail.mp4",
        "category": "Signature",
        "description": "Proof that the best cocktails need only a few ingredients — a perfectly balanced drink that lets quality spirits shine.",
        "cocktail_id": None,
        "tags": ["Simple", "Beginner", "Spirit-Forward", "Quick"],
        "difficulty": "Easy"
    },
    # ── French & Continental ───────────────
    "french_martini": {
        "title": "French Martini",
        "filename": "french_martini.mp4",
        "category": "Martini",
        "description": "Vodka, Chambord raspberry liqueur, and pineapple juice — shaken to a gorgeous pink froth. Fruity, elegant, and deeply satisfying.",
        "cocktail_id": None,
        "tags": ["Vodka", "Raspberry", "Shaken", "Fruity"],
        "difficulty": "Easy"
    },
    # ── Blue & Tropical ────────────────────
    "blue_paradise": {
        "title": "Blue Paradise",
        "filename": "blue_paradise.mp4",
        "category": "Tropical",
        "description": "A vibrant ocean-blue tropical cocktail — light rum, blue curacao, and coconut water shaken over ice. Paradise in a glass.",
        "cocktail_id": None,
        "tags": ["Rum", "Blue Curacao", "Tropical", "Vibrant"],
        "difficulty": "Easy"
    },
    "blue_lagoon": {
        "title": "Blue Lagoon",
        "filename": "blue_lagoon.mp4",
        "category": "Tropical",
        "description": "Electric blue and refreshingly tropical — vodka, blue curacao, and lemonade create a drink as beautiful as a Caribbean lagoon.",
        "cocktail_id": None,
        "tags": ["Vodka", "Blue Curacao", "Built", "Tropical"],
        "difficulty": "Easy"
    },
    "blue_lagoon_classic": {
        "title": "Blue Lagoon Classic",
        "filename": "blue_lagoon_classic.mp4",
        "category": "Tropical",
        "description": "The original Blue Lagoon recipe — a stunning azure cocktail that has been delighting guests since the 1970s.",
        "cocktail_id": None,
        "tags": ["Vodka", "Blue Curacao", "Classic", "Retro"],
        "difficulty": "Easy"
    },
    "blue_lagoon_frosty": {
        "title": "Blue Lagoon Frosty",
        "filename": "blue_lagoon_frosty.mp4",
        "category": "Tropical",
        "description": "A frozen blended version of the Blue Lagoon — icy, slushy, and impossibly refreshing for hot days by the pool.",
        "cocktail_id": None,
        "tags": ["Blended", "Frozen", "Blue Curacao", "Party"],
        "difficulty": "Easy"
    },
    "blue_lady": {
        "title": "Blue Lady",
        "filename": "blue_lady.mp4",
        "category": "Tropical",
        "description": "A sophisticated blue gin cocktail — blue curacao, lemon, and gin shaken to a gorgeous sapphire hue with a silky texture.",
        "cocktail_id": None,
        "tags": ["Gin", "Blue Curacao", "Shaken", "Elegant"],
        "difficulty": "Medium"
    },
    # ── Strawberry & Fruit ─────────────────
    "strawberry_cocktail": {
        "title": "Strawberry Cocktail",
        "filename": "strawberry_cocktail.mp4",
        "category": "Fruit",
        "description": "Fresh muddled strawberries shaken with vodka, lemon, and a touch of vanilla — summery, vibrant, and beautifully pink.",
        "cocktail_id": None,
        "tags": ["Vodka", "Strawberry", "Muddled", "Summer"],
        "difficulty": "Easy"
    },
    "coconut_sunset": {
        "title": "Coconut Sunset",
        "filename": "coconut_sunset.mp4",
        "category": "Fruit",
        "description": "Layers of coconut rum, pineapple juice, and grenadine create a breathtaking sunset gradient — tropical and deeply indulgent.",
        "cocktail_id": None,
        "tags": ["Coconut Rum", "Pineapple", "Layered", "Tropical"],
        "difficulty": "Medium"
    },
    # ── Social & Trending ──────────────────
    "fresh_cocktail": {
        "title": "Fresh Cocktail",
        "filename": "fresh_cocktail.mp4",
        "category": "Trending",
        "description": "A vibrant, herb-forward cocktail built around the freshest seasonal ingredients — the kind of drink that photographs beautifully.",
        "cocktail_id": None,
        "tags": ["Fresh", "Herbs", "Seasonal", "Instagram"],
        "difficulty": "Medium"
    },
    "garibaldi": {
        "title": "Garibaldi",
        "filename": "garibaldi.mp4",
        "category": "Trending",
        "description": "Italy's cult two-ingredient cocktail — Campari topped with fluffy, freshly juiced orange juice. Simple, bitter, and sensational.",
        "cocktail_id": None,
        "tags": ["Campari", "Orange Juice", "Built", "Italian"],
        "difficulty": "Easy"
    },
    "hot_girl_summer_spritz": {
        "title": "Hot Girl Summer Spritz",
        "filename": "hot_girl_summer_spritz.mp4",
        "category": "Trending",
        "description": "A pastel pink summer spritz built for golden hour — Aperol, rose wine, peach, and prosecco in a tall ice-filled glass.",
        "cocktail_id": None,
        "tags": ["Aperol", "Rose", "Spritz", "Summer"],
        "difficulty": "Easy"
    },
    "delicious_cocktail": {
        "title": "Delicious Cocktail",
        "filename": "delicious_cocktail.mp4",
        "category": "Trending",
        "description": "A crowd-pleasing, well-balanced cocktail that proves great drinks don't have to be complicated — just delicious.",
        "cocktail_id": None,
        "tags": ["Easy", "Balanced", "Crowd Pleaser", "Beginner"],
        "difficulty": "Easy"
    },
    "cocktail_reply": {
        "title": "Cocktail Reply",
        "filename": "cocktail_reply.mp4",
        "category": "Trending",
        "description": "A viral social media cocktail created in direct response to a viewer request — community-driven and full of character.",
        "cocktail_id": None,
        "tags": ["Viral", "Social Media", "Community", "Trending"],
        "difficulty": "Medium"
    },
    # ── Special & Artisan ──────────────────
    "ramos_gin": {
        "title": "Ramos Gin Fizz",
        "filename": "Ramos_Gin.mp4",
        "category": "Artisan",
        "description": "New Orleans' most legendary cocktail — gin, cream, egg white, orange blossom water, and citrus shaken for a full 12 minutes to achieve its iconic cloud-like foam.",
        "cocktail_id": None,
        "tags": ["Gin", "Egg White", "Cream", "New Orleans"],
        "difficulty": "Advanced"
    },
    "bees_knees": {
        "title": "Bee's Knees",
        "filename": "bees_knees.mp4",
        "category": "Artisan",
        "description": "A Prohibition-era gin cocktail sweetened with honey syrup and balanced with fresh lemon — smooth, aromatic, and timeless.",
        "cocktail_id": "bees_knees",
        "tags": ["Gin", "Honey", "Shaken", "Prohibition"],
        "difficulty": "Easy"
    },
    "arctic_glow": {
        "title": "Arctic Glow",
        "filename": "Arctic_Glow.mp4",
        "category": "Artisan",
        "description": "A visually stunning ice-blue cocktail — gin, elderflower, and butterfly pea flower create a luminous arctic shimmer that changes colour with citrus.",
        "cocktail_id": None,
        "tags": ["Gin", "Elderflower", "Butterfly Pea", "Colour Changing"],
        "difficulty": "Advanced"
    },
    "sex_on_the_beach": {
        "title": "Sex on the Beach",
        "filename": "sex_on_the_beach.mp4",
        "category": "Classic",
        "description": "A fruity and fun classic — vodka, peach schnapps, cranberry, and orange juice layered in a tall glass. The ultimate 90s party cocktail.",
        "cocktail_id": "sex_on_the_beach",
        "tags": ["Vodka", "Peach", "Fruity", "Party"],
        "difficulty": "Easy"
    }
}

# ─────────────────────────────────────────
#  Background Media Data
# ─────────────────────────────────────────
background = {
    "hero": {
        "videos": ["https://cdn.pixabay.com/video/2025/12/18/322790_medium.mp4"],
        "images": []
    },
    "bar": {
        "videos": [
            "https://assets.mixkit.co/videos/4043/4043-360.mp4",   # A busy elegant bar
            "https://assets.mixkit.co/videos/8711/8711-360.mp4"    # Beer bar atmosphere
        ],
        "images": []
    },
    "shaker": {
        "videos": [
            "https://assets.mixkit.co/videos/4174/4174-360.mp4"    # Barista waving a cocktail shaker
        ],
        "images": []
    },
    "pouring": {
        "videos": [
            "https://assets.mixkit.co/videos/4173/4173-360.mp4"    # Bartender preparing and pouring a cocktail
        ],
        "images": []
    },
    "garnish": {
        "videos": [
            "https://assets.mixkit.co/videos/15171/15171-360.mp4"  # Bartender decorating drink glasses
        ],
        "images": []
    },
    "ambience": {
        "videos": [
            "https://assets.mixkit.co/videos/27819/27819-360.mp4", # Tropical cocktail glass at sunset
            "https://assets.mixkit.co/videos/25458/25458-360.mp4"  # Two cocktails on the beach
        ],
        "images": []
    },
    "glassware": {
        "videos": [
            "https://assets.mixkit.co/videos/22848/22848-360.mp4", # Margarita glass with salt rim close-up
            "https://assets.mixkit.co/videos/22850/22850-360.mp4"  # Smoking cocktail glass
        ],
        "images": []
    },
    "ingredients": {
        "videos": [
            "https://assets.mixkit.co/videos/4295/4295-360.mp4",   # Barmaid preparing cocktail with bottles
            "https://assets.mixkit.co/videos/40487/40487-360.mp4"  # Close-up cocktail with fresh berry ingredients
        ],
        "images": []
    },
    "cocktail_making": {
        "videos": [
            "https://assets.mixkit.co/videos/43962/43962-360.mp4", # Serving a prepared cocktail at the bar
            "https://assets.mixkit.co/videos/4173/4173-360.mp4"    # Bartender mixing a cocktail
        ],
        "images": []
    }
}


# ─────────────────────────────────────────
#  Helper
# ─────────────────────────────────────────
def format_cocktail(key, cocktail, image=None):
    images = cocktail["images"]

    # If no local images, fetch from TheCocktailDB as fallback
    if not images:
        fallback = get_fallback_image(key)
        if fallback:
            images = [fallback]

    return {
        "id": key,
        "name": key.replace("_", " ").title(),
        "description": cocktail["description"],
        "ingredients": cocktail["ingredients"],
        "image": image or (random.choice(images) if images else None),
        "images": images,
        "total_ingredients": len(cocktail["ingredients"])
    }


# ─────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────

@app.route("/")
def home():
    return jsonify({
        "message": "🍹 Cocktail API is running!",
        "total_cocktails": len(cocktails),
        "total_backgrounds": len(background),
        "total_histories": len(cocktail_history),
        "total_pairings": len(food_pairings),
        "total_mocktails": len(mocktails),
        "total_videos": len(cocktail_videos),
        "endpoints": {
            "GET /api/cocktails": "List all cocktails (supports ?search=, ?ingredient=, ?limit=, ?offset=)",
            "GET /api/cocktail/<n>": "Get cocktail by name (random image)",
            "GET /api/cocktail/<n>/images": "Get all images for a cocktail",
            "GET /api/cocktails/random": "Get a random cocktail",
            "GET /api/cocktails/names": "Get all cocktail names/IDs",
            "GET /api/backgrounds": "Get all background media",
            "GET /api/background/<n>": "Get a specific background by name (e.g. hero, bar, pouring)",
            "GET /api/histories": "Get all cocktail history entries",
            "GET /api/history/<n>": "Get history for a specific cocktail (e.g. negroni, martini)",
            "GET /api/histories/random": "Get a random cocktail history entry",
            "GET /api/pairings": "Get all food pairing entries (supports ?category=)",
            "GET /api/pairing/<n>": "Get cocktail pairings for a specific dish (e.g. wagyu_beef, sashimi)",
            "GET /api/pairings/random": "Get a random food pairing entry",
            "GET /api/pairings/categories": "Get all available food categories",
            "GET /api/mocktails": "Get all mocktails & zero-proof drinks (supports ?flavour=)",
            "GET /api/mocktail/<n>": "Get a specific mocktail (e.g. virgin_mojito, hibiscus_spritz)",
            "GET /api/mocktails/random": "Get a random mocktail",
            "GET /api/videos": "Get all cocktail videos (supports ?category=, ?difficulty=, ?tag=)",
            "GET /api/video/<n>": "Get a specific video entry (e.g. negroni, smoked_old_fashioned)",
            "GET /api/videos/random": "Get a random video entry",
            "GET /api/videos/categories": "Get all video categories"
        }
    })


@app.route("/api/cocktails")
def get_all_cocktails():
    search = request.args.get("search", "").lower()
    ingredient_filter = request.args.get("ingredient", "").lower()
    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", 0, type=int)

    results = []
    for key, cocktail in cocktails.items():
        # Filter by name search
        if search and search not in key.replace("_", " ") and search not in cocktail["description"].lower():
            continue
        # Filter by ingredient
        if ingredient_filter:
            ingredients_lower = [i.lower() for i in cocktail["ingredients"]]
            if not any(ingredient_filter in i for i in ingredients_lower):
                continue
        results.append(format_cocktail(key, cocktail))

    total = len(results)
    results = results[offset:]
    if limit:
        results = results[:limit]

    return jsonify({
        "total": total,
        "offset": offset,
        "limit": limit,
        "count": len(results),
        "cocktails": results
    })


@app.route("/api/cocktails/names")
def get_names():
    return jsonify({
        "total": len(cocktails),
        "cocktails": [
            {"id": key, "name": key.replace("_", " ").title()}
            for key in cocktails
        ]
    })


@app.route("/api/cocktails/random")
def get_random():
    key = random.choice(list(cocktails.keys()))
    cocktail = cocktails[key]
    return jsonify(format_cocktail(key, cocktail))


@app.route("/api/cocktail/<name>")
def get_cocktail(name):
    key = name.lower().replace(" ", "_").replace("-", "_")
    cocktail = cocktails.get(key)
    if not cocktail:
        return jsonify({
            "error": f"Cocktail '{name}' not found.",
            "suggestion": "Use GET /api/cocktails/names to see all available cocktails."
        }), 404
    return jsonify(format_cocktail(key, cocktail))


@app.route("/api/cocktail/<name>/images")
def get_images(name):
    key = name.lower().replace(" ", "_").replace("-", "_")
    cocktail = cocktails.get(key)
    if not cocktail:
        return jsonify({"error": f"Cocktail '{name}' not found."}), 404
    return jsonify({
        "id": key,
        "name": key.replace("_", " ").title(),
        "images": cocktail["images"]
    })



# ─────────────────────────────────────────
#  Background Routes
# ─────────────────────────────────────────

@app.route("/api/backgrounds")
def get_all_backgrounds():
    return jsonify({
        "total": len(background),
        "backgrounds": {
            key: {
                "id": key,
                "name": key.replace("_", " ").title(),
                "videos": val["videos"],
                "images": val["images"],
                "total_videos": len(val["videos"]),
                "total_images": len(val["images"])
            }
            for key, val in background.items()
        }
    })


@app.route("/api/background/<name>")
def get_background(name):
    key = name.lower().replace(" ", "_").replace("-", "_")
    bg = background.get(key)
    if not bg:
        return jsonify({
            "error": f"Background '{name}' not found.",
            "available": list(background.keys())
        }), 404
    return jsonify({
        "id": key,
        "name": key.replace("_", " ").title(),
        "videos": bg["videos"],
        "images": bg["images"],
        "total_videos": len(bg["videos"]),
        "total_images": len(bg["images"])
    })



# ─────────────────────────────────────────
#  Cocktail History Routes
# ─────────────────────────────────────────

@app.route("/api/histories")
def get_all_histories():
    return jsonify({
        "total": len(cocktail_history),
        "histories": list(cocktail_history.values())
    })


@app.route("/api/history/<n>")
def get_history(name):
    key = name.lower().replace(" ", "_").replace("-", "_")
    history = cocktail_history.get(key)
    if not history:
        return jsonify({
            "error": f"History for '{name}' not found.",
            "available": list(cocktail_history.keys())
        }), 404
    return jsonify(history)


@app.route("/api/histories/random")
def get_random_history():
    key = random.choice(list(cocktail_history.keys()))
    return jsonify(cocktail_history[key])



# ─────────────────────────────────────────
#  Food Pairing Routes
# ─────────────────────────────────────────

@app.route("/api/pairings")
def get_all_pairings():
    category_filter = request.args.get("category", "").lower()
    results = []
    for key, pairing in food_pairings.items():
        if category_filter and category_filter not in pairing["category"].lower():
            continue
        results.append({**pairing, "id": key})
    return jsonify({
        "total": len(results),
        "pairings": results
    })


@app.route("/api/pairing/<n>")
def get_pairing(name):
    key = name.lower().replace(" ", "_").replace("-", "_")
    pairing = food_pairings.get(key)
    if not pairing:
        return jsonify({
            "error": f"Pairing for '{name}' not found.",
            "available": list(food_pairings.keys())
        }), 404
    return jsonify({**pairing, "id": key})


@app.route("/api/pairings/random")
def get_random_pairing():
    key = random.choice(list(food_pairings.keys()))
    return jsonify({**food_pairings[key], "id": key})


@app.route("/api/pairings/categories")
def get_pairing_categories():
    categories = {}
    for key, pairing in food_pairings.items():
        cat = pairing["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({"id": key, "name": pairing["name"]})
    return jsonify({
        "total_categories": len(categories),
        "categories": categories
    })



# ─────────────────────────────────────────
#  Mocktail & Zero-Proof Routes
# ─────────────────────────────────────────

def format_mocktail(key, drink):
    return {
        "id": key,
        "name": key.replace("_", " ").title(),
        "description": drink["description"],
        "ingredients": drink["ingredients"],
        "image": random.choice(drink["images"]) if drink["images"] else None,
        "zero_proof": drink["zero_proof"],
        "flavour_profile": drink["flavour_profile"],
        "total_ingredients": len(drink["ingredients"])
    }


@app.route("/api/mocktails")
def get_all_mocktails():
    flavour_filter = request.args.get("flavour", "").lower()
    results = []
    for key, drink in mocktails.items():
        if flavour_filter:
            profiles_lower = [f.lower() for f in drink["flavour_profile"]]
            if not any(flavour_filter in f for f in profiles_lower):
                continue
        results.append(format_mocktail(key, drink))
    return jsonify({
        "total": len(results),
        "mocktails": results
    })


@app.route("/api/mocktail/<n>")
def get_mocktail(name):
    key = name.lower().replace(" ", "_").replace("-", "_")
    drink = mocktails.get(key)
    if not drink:
        return jsonify({
            "error": f"Mocktail '{name}' not found.",
            "available": list(mocktails.keys())
        }), 404
    return jsonify(format_mocktail(key, drink))


@app.route("/api/mocktails/random")
def get_random_mocktail():
    key = random.choice(list(mocktails.keys()))
    return jsonify(format_mocktail(key, mocktails[key]))



# ─────────────────────────────────────────
#  Cocktail Video Routes
# ─────────────────────────────────────────

def format_video(key, video):
    return {
        "id": key,
        "title": video["title"],
        "filename": video["filename"],
        "url": VIDEO_BASE_URL + video["filename"],
        "category": video["category"],
        "description": video["description"],
        "cocktail_id": video.get("cocktail_id"),
        "tags": video["tags"],
        "difficulty": video["difficulty"]
    }


@app.route("/api/videos")
def get_all_videos():
    category_filter  = request.args.get("category",   "").lower()
    difficulty_filter = request.args.get("difficulty", "").lower()
    tag_filter       = request.args.get("tag",        "").lower()

    results = []
    for key, video in cocktail_videos.items():
        if category_filter and category_filter not in video["category"].lower():
            continue
        if difficulty_filter and difficulty_filter not in video["difficulty"].lower():
            continue
        if tag_filter:
            tags_lower = [t.lower() for t in video["tags"]]
            if not any(tag_filter in t for t in tags_lower):
                continue
        results.append(format_video(key, video))

    return jsonify({
        "total": len(results),
        "video_base_url": VIDEO_BASE_URL,
        "videos": results
    })


@app.route("/api/video/<n>")
def get_video(name):
    key = name.lower().replace(" ", "_").replace("-", "_")
    video = cocktail_videos.get(key)
    if not video:
        return jsonify({
            "error": f"Video for '{name}' not found.",
            "available": list(cocktail_videos.keys())
        }), 404
    return jsonify(format_video(key, video))


@app.route("/api/videos/random")
def get_random_video():
    key = random.choice(list(cocktail_videos.keys()))
    return jsonify(format_video(key, cocktail_videos[key]))


@app.route("/api/videos/categories")
def get_video_categories():
    categories = {}
    for key, video in cocktail_videos.items():
        cat = video["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "id": key,
            "title": video["title"],
            "difficulty": video["difficulty"],
            "url": VIDEO_BASE_URL + video["filename"]
        })
    return jsonify({
        "total_categories": len(categories),
        "categories": categories
    })


# ─────────────────────────────────────────
#  404 fallback
# ─────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found. Visit / for available endpoints."}), 404


if __name__ == "__main__":
    app.run(debug=False)