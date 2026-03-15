from flask import Flask, jsonify, request
import random
import requests as req
import os

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
        "images": ["https://www.liquor.com/thmb/P9lQ1-ePDlYhfPA-kYRvM-G-ezM=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/cupids-champagne-potion-720x720-primary-a9eebba81d9343d8870c9054636c1094.jpg"]
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
        "image": "https://www.liquor.com/thmb/g4on6L9ECJf_1WJO3Uxf5hOmCFQ=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/__opt__aboutcom__coeus__resources__content_migration__liquor__2018__08__14074619__bentons-old-fashioned-720x720-recipe-acc67854ebf54e9597329cc81f75e4c5.jpg"
    },
    "martini": {
        "name": "Martini",
        "year": "1880s",
        "origin": "United States",
        "era": "Gilded Age",
        "summary": "The Martini's exact origin is disputed — some trace it to Martinez, California in the 1860s, while others credit New York bartenders in the 1880s. Originally made with sweet vermouth and gin, it evolved into the drier version we know today. By the 1920s it became the defining drink of sophistication. Ernest Hemingway, Winston Churchill, and Dorothy Parker all had famously strong opinions about the perfect Martini ratio.",
        "fun_fact": "Winston Churchill's preferred method was to simply glance at a bottle of vermouth across the room while drinking his gin — he liked his Martini bone dry.",
        "image": "https://www.liquor.com/thmb/js3M99n5Oz1C2WmNyX1idOAgZPw=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/wet-martini-1500x1500-hero-9de0178e0e84444da2f6bcecf367e79d.jpg"
    },
    "negroni": {
        "name": "Negroni",
        "year": "1919",
        "origin": "Florence, Italy",
        "era": "Post-WWI",
        "summary": "The Negroni was born in Florence, Italy in 1919 when Count Camillo Negroni asked bartender Fosco Scarselli to strengthen his Americano by replacing soda water with gin. The bartender also switched the orange slice for an orange peel to signify it was a different drink. The Count's family later opened the Negroni distillery to produce a ready-made version of the cocktail, cementing its place in history.",
        "fun_fact": "The Negroni is one of the few cocktails named after a real person who actually invented it — most cocktail origin stories are disputed myths.",
        "image": "https://www.liquor.com/thmb/DNlcQmIP9a1RXMaV3-SeDZx6PGs=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/dutch-negroni-720x720-primary-f5660be0f0e6455398f0d702a4493484.jpg"
    },
    "manhattan": {
        "name": "Manhattan",
        "year": "1874",
        "origin": "New York City, USA",
        "era": "Gilded Age",
        "summary": "The Manhattan is said to have been created at the Manhattan Club in New York City around 1874, allegedly for a banquet hosted by Lady Randolph Churchill — mother of Winston Churchill. However historians note she was likely in England at the time, pregnant. The true origin remains debated, but what is certain is that by the 1880s the Manhattan was already one of the most popular cocktails in America, setting the template for all stirred, spirit-forward cocktails.",
        "fun_fact": "The Manhattan is believed to be the first cocktail to use vermouth as a key ingredient, sparking the entire vermouth cocktail category.",
        "image": "https://www.liquor.com/thmb/gR-5gqkopJz_RJv2SLbSMrkefRk=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/canadian-manhattan-720x720-primary-875aa449d1d44a6a99b200536778f46c.jpg"
    },
    "mojito": {
        "name": "Mojito",
        "year": "1500s",
        "origin": "Havana, Cuba",
        "era": "Colonial Era",
        "summary": "The Mojito traces its roots to 16th century Cuba. Sir Francis Drake's crew used a primitive version called 'El Draque' — made with aguardiente, mint, lime, and sugar — to combat scurvy and dysentery. As Cuban rum improved in quality, aguardiente was replaced, and the modern Mojito was born. It became internationally famous when Ernest Hemingway adopted it as his drink of choice at La Bodeguita del Medio bar in Havana during the 1940s and 50s.",
        "fun_fact": "Ernest Hemingway wrote on the wall of La Bodeguita del Medio: 'My mojito in La Bodeguita, my daiquiri in El Floridita' — though some historians believe this was a marketing invention.",
        "image": "https://www.liquor.com/thmb/_n9KvoH9Asqqmk9P5CgY7m4rg8c=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/winter-mojito-720x720-primary-8349af7d91964c7b99df103c59758193.jpg"
    },
    "daiquiri": {
        "name": "Daiquiri",
        "year": "1898",
        "origin": "Daiquiri, Cuba",
        "era": "Spanish-American War Era",
        "summary": "The Daiquiri was invented by American mining engineer Jennings Cox near the town of Daiquiri, Cuba in 1898. Running low on gin to serve guests, Cox mixed local rum with lime juice and sugar — and the Daiquiri was born. Naval officer Lucius Johnson brought the recipe to the Army and Navy Club in Washington D.C., spreading it across the United States. During WWII, whisky and other spirits were rationed, making rum-based Daiquiris enormously popular.",
        "fun_fact": "JFK was such a fan of Daiquiris that the drink reportedly became fashionable among Washington's political elite during his presidency.",
        "image": "https://www.liquor.com/thmb/oxW0VcGagmzGWaAsEUZi1W-4arE=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/Frozen-Daiquiri-1500x1500-hero-ee5a125ec0d04488a52a32db6278f3da.jpg"
    },
    "margarita": {
        "name": "Margarita",
        "year": "1938",
        "origin": "Mexico / USA Border",
        "era": "Prohibition Aftermath",
        "summary": "The Margarita has at least seven disputed origin stories. The most widely accepted credits socialite Margarita Sames who created it at her Acapulco villa in 1948. Others credit Dallas restaurant owner Santos Cruz who made it for singer Peggy Lee in 1948, or bartender Danny Herrera who created it for actress Marjorie King in 1938. Regardless of origin, by the 1950s it was appearing in magazines, and by the 1970s it had become America's most ordered cocktail.",
        "fun_fact": "The frozen Margarita machine was invented by Dallas restaurateur Mariano Martinez in 1971, inspired by a 7-Eleven Slurpee machine.",
        "image": "https://www.liquor.com/thmb/V5L3hv-w8ph2_RQi_-simg-4Ris=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/Frozen-Margarita-1500x1500-hero-191e49b3ab4f4781b93f3cfacac25136.jpg"
    },
    "singapore_sling": {
        "name": "Singapore Sling",
        "year": "1915",
        "origin": "Singapore",
        "era": "Colonial Era",
        "summary": "The Singapore Sling was created around 1915 by bartender Ngiam Tong Boon at the Long Bar of Raffles Hotel in Singapore. At the time, it was considered improper for women to drink alcohol in public, so Ngiam crafted a cocktail that resembled fruit punch — allowing women to drink discreetly. The pink, fruity drink was a social revolution in its time. The original recipe was lost and rediscovered in the 1970s from a scribbled note found in the hotel's safe.",
        "fun_fact": "Raffles Hotel still serves over 1,000 Singapore Slings per day, making it one of the most consistently ordered cocktails at a single venue in the world.",
        "image": "https://www.liquor.com/thmb/g82LDbrf49zzbv9gHNnbouuaggE=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/Singapore_Sling_3000x3000_primary-5fd9e3d361204753919604d123ca23f2.jpg"
    },
    "sazerac": {
        "name": "Sazerac",
        "year": "1838",
        "origin": "New Orleans, USA",
        "era": "Antebellum America",
        "summary": "The Sazerac is often called America's first cocktail. It was created in New Orleans around 1838 by Antoine Amedie Peychaud, a Creole apothecary who served brandy toddies with his own bitters in an egg cup called a 'coquetier' — which Americans mispronounced as 'cocktay', possibly giving us the word 'cocktail'. The drink evolved to use rye whisky after a phylloxera epidemic wiped out European cognac production in the 1870s. New Orleans declared it the city's official cocktail in 2008.",
        "fun_fact": "The Sazerac may have inadvertently given us the word 'cocktail' — Peychaud's egg cup coquetier allegedly became the mispronounced origin of the term.",
        "image": "https://www.liquor.com/thmb/qAybJQUD4Cx2L1XvYj3HREQhXBQ=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/sazerac-1500x1500-hero-62326d995cdb4a79a6a0a3bd4a98cef9.jpg"
    },
    "mai_tai": {
        "name": "Mai Tai",
        "year": "1944",
        "origin": "Oakland, California, USA",
        "era": "Post-WWII Tiki Era",
        "summary": "The Mai Tai was invented in 1944 by Trader Vic (Victor Bergeron) at his restaurant in Oakland, California. He shook up the drink for two friends visiting from Tahiti — Ham and Carrie Guild. Upon tasting it, Carrie reportedly exclaimed 'Mai Tai — Roa Ae!' meaning 'Out of this world — the best!' in Tahitian, and the drink had its name. The Mai Tai became the signature drink of the entire Tiki cocktail movement that swept America in the post-WWII era.",
        "fun_fact": "Donn Beach (Don the Beachcomber) claimed he invented the Mai Tai earlier, sparking a lifelong rivalry with Trader Vic that was never officially resolved.",
        "image": "https://www.liquor.com/thmb/m6rry9JJhbW1yj70uzJzTXjwhW8=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/__opt__aboutcom__coeus__resources__content_migration__liquor__2010__02__queen-elizabeth-08f5ffde13c14a57ab3ca9f32c724b2b.jpg"
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
            "GET /api/histories/random": "Get a random cocktail history entry"
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
#  404 fallback
# ─────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found. Visit / for available endpoints."}), 404



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)