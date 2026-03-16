from flask import Flask, jsonify, request
import random
import requests as req

app = Flask(__name__)

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
#  Cocktail History Data (10 iconic cocktails)
#  Images served from: static/cocktail_history/
# ─────────────────────────────────────────
HISTORY_IMAGE_BASE = "/static/cocktail_history/"

cocktail_history = {
    "old_fashioned": {
        "name": "Old Fashioned",
        "year": "1806",
        "origin": "United States",
        "era": "19th Century",
        "summary": "The Old Fashioned is widely considered the original cocktail. The word 'cocktail' was first defined in 1806 as a mix of spirits, sugar, water, and bitters — which is exactly what an Old Fashioned is. By the 1880s, bartenders began adding unnecessary garnishes and liqueurs, prompting patrons to request their drink made the 'old fashioned' way. The name stuck. It remains one of the most ordered cocktails in the world.",
        "fun_fact": "President Franklin D. Roosevelt reportedly celebrated the end of Prohibition in 1933 by mixing Old Fashioneds for his staff.",
        "image": HISTORY_IMAGE_BASE + "old_fashioned_history.png"
    },
    "martini": {
        "name": "Martini",
        "year": "1880s",
        "origin": "United States",
        "era": "Gilded Age",
        "summary": "The Martini's exact origin is disputed — some trace it to Martinez, California in the 1860s, while others credit New York bartenders in the 1880s. Originally made with sweet vermouth and gin, it evolved into the drier version we know today. By the 1920s it became the defining drink of sophistication. Ernest Hemingway, Winston Churchill, and Dorothy Parker all had famously strong opinions about the perfect Martini ratio.",
        "fun_fact": "Winston Churchill's preferred method was to simply glance at a bottle of vermouth across the room while drinking his gin — he liked his Martini bone dry.",
        "image": HISTORY_IMAGE_BASE + "martini.png"
    },
    "negroni": {
        "name": "Negroni",
        "year": "1919",
        "origin": "Florence, Italy",
        "era": "Post-WWI",
        "summary": "The Negroni was born in Florence, Italy in 1919 when Count Camillo Negroni asked bartender Fosco Scarselli to strengthen his Americano by replacing soda water with gin. The bartender also switched the orange slice for an orange peel to signify it was a different drink. The Count's family later opened the Negroni distillery to produce a ready-made version of the cocktail, cementing its place in history.",
        "fun_fact": "The Negroni is one of the few cocktails named after a real person who actually invented it — most cocktail origin stories are disputed myths.",
        "image": HISTORY_IMAGE_BASE + "negroni.png"
    },
    "manhattan": {
        "name": "Manhattan",
        "year": "1874",
        "origin": "New York City, USA",
        "era": "Gilded Age",
        "summary": "The Manhattan is said to have been created at the Manhattan Club in New York City around 1874, allegedly for a banquet hosted by Lady Randolph Churchill — mother of Winston Churchill. However historians note she was likely in England at the time, pregnant. The true origin remains debated, but what is certain is that by the 1880s the Manhattan was already one of the most popular cocktails in America, setting the template for all stirred, spirit-forward cocktails.",
        "fun_fact": "The Manhattan is believed to be the first cocktail to use vermouth as a key ingredient, sparking the entire vermouth cocktail category.",
        "image": HISTORY_IMAGE_BASE + "manhattan.png"
    },
    "mojito": {
        "name": "Mojito",
        "year": "1500s",
        "origin": "Havana, Cuba",
        "era": "Colonial Era",
        "summary": "The Mojito traces its roots to 16th century Cuba. Sir Francis Drake's crew used a primitive version called 'El Draque' — made with aguardiente, mint, lime, and sugar — to combat scurvy and dysentery. As Cuban rum improved in quality, aguardiente was replaced, and the modern Mojito was born. It became internationally famous when Ernest Hemingway adopted it as his drink of choice at La Bodeguita del Medio bar in Havana during the 1940s and 50s.",
        "fun_fact": "Ernest Hemingway wrote on the wall of La Bodeguita del Medio: 'My mojito in La Bodeguita, my daiquiri in El Floridita' — though some historians believe this was a marketing invention.",
        "image": HISTORY_IMAGE_BASE + "mojito.png"
    },
    "daiquiri": {
        "name": "Daiquiri",
        "year": "1898",
        "origin": "Daiquiri, Cuba",
        "era": "Spanish-American War Era",
        "summary": "The Daiquiri was invented by American mining engineer Jennings Cox near the town of Daiquiri, Cuba in 1898. Running low on gin to serve guests, Cox mixed local rum with lime juice and sugar — and the Daiquiri was born. Naval officer Lucius Johnson brought the recipe to the Army and Navy Club in Washington D.C., spreading it across the United States. During WWII, whisky and other spirits were rationed, making rum-based Daiquiris enormously popular.",
        "fun_fact": "JFK was such a fan of Daiquiris that the drink reportedly became fashionable among Washington's political elite during his presidency.",
        "image": HISTORY_IMAGE_BASE + "daiquiri.png"
    },
    "margarita": {
        "name": "Margarita",
        "year": "1938",
        "origin": "Mexico / USA Border",
        "era": "Prohibition Aftermath",
        "summary": "The Margarita has at least seven disputed origin stories. The most widely accepted credits socialite Margarita Sames who created it at her Acapulco villa in 1948. Others credit Dallas restaurant owner Santos Cruz who made it for singer Peggy Lee in 1948, or bartender Danny Herrera who created it for actress Marjorie King in 1938. Regardless of origin, by the 1950s it was appearing in magazines, and by the 1970s it had become America's most ordered cocktail.",
        "fun_fact": "The frozen Margarita machine was invented by Dallas restaurateur Mariano Martinez in 1971, inspired by a 7-Eleven Slurpee machine.",
        "image": HISTORY_IMAGE_BASE + "margarita.png"
    },
    "singapore_sling": {
        "name": "Singapore Sling",
        "year": "1915",
        "origin": "Singapore",
        "era": "Colonial Era",
        "summary": "The Singapore Sling was created around 1915 by bartender Ngiam Tong Boon at the Long Bar of Raffles Hotel in Singapore. At the time, it was considered improper for women to drink alcohol in public, so Ngiam crafted a cocktail that resembled fruit punch — allowing women to drink discreetly. The pink, fruity drink was a social revolution in its time. The original recipe was lost and rediscovered in the 1970s from a scribbled note found in the hotel's safe.",
        "fun_fact": "Raffles Hotel still serves over 1,000 Singapore Slings per day, making it one of the most consistently ordered cocktails at a single venue in the world.",
        "image": HISTORY_IMAGE_BASE + "singapore_sling.png"
    },
    "sazerac": {
        "name": "Sazerac",
        "year": "1838",
        "origin": "New Orleans, USA",
        "era": "Antebellum America",
        "summary": "The Sazerac is often called America's first cocktail. It was created in New Orleans around 1838 by Antoine Amedie Peychaud, a Creole apothecary who served brandy toddies with his own bitters in an egg cup called a 'coquetier' — which Americans mispronounced as 'cocktay', possibly giving us the word 'cocktail'. The drink evolved to use rye whisky after a phylloxera epidemic wiped out European cognac production in the 1870s. New Orleans declared it the city's official cocktail in 2008.",
        "fun_fact": "The Sazerac may have inadvertently given us the word 'cocktail' — Peychaud's egg cup coquetier allegedly became the mispronounced origin of the term.",
        "image": HISTORY_IMAGE_BASE + "sazerac.png"
    },
    "mai_tai": {
        "name": "Mai Tai",
        "year": "1944",
        "origin": "Oakland, California, USA",
        "era": "Post-WWII Tiki Era",
        "summary": "The Mai Tai was invented in 1944 by Trader Vic (Victor Bergeron) at his restaurant in Oakland, California. He shook up the drink for two friends visiting from Tahiti — Ham and Carrie Guild. Upon tasting it, Carrie reportedly exclaimed 'Mai Tai — Roa Ae!' meaning 'Out of this world — the best!' in Tahitian, and the drink had its name. The Mai Tai became the signature drink of the entire Tiki cocktail movement that swept America in the post-WWII era.",
        "fun_fact": "Donn Beach (Don the Beachcomber) claimed he invented the Mai Tai earlier, sparking a lifelong rivalry with Trader Vic that was never officially resolved.",
        "image": HISTORY_IMAGE_BASE + "mai_tai.png"
    }
}

# ─────────────────────────────────────────
#  Food Pairing Data (25 dishes)
#  Videos served from: static/food_pairing_videos/
# ─────────────────────────────────────────
FOOD_VIDEO_BASE = "/static/food_pairing_videos/"
COCKTAIL_IMAGE_BASE = "/static/cocktail_pairing_images/"

food_pairings = {
    "wagyu_beef": {
        "name": "Wagyu Beef",
        "category": "Meat",
        "description": "Exceptionally marbled Japanese beef with an intensely buttery, umami-rich flavour and a melt-in-the-mouth texture. The high fat content calls for cocktails that cut through richness while complementing its depth.",
        "flavour_profile": ["Rich", "Buttery", "Umami", "Savoury"],
        "video": FOOD_VIDEO_BASE + "wagyu_beef.mp4",
        "pairings": [
            {
                "cocktail": "Old Fashioned",
                "cocktail_id": "old_fashioned",
                "reason": "Bourbon's caramel and vanilla notes mirror the beef's richness, while the bitters cut through the fat and cleanse the palate between bites.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Old Fashioned.jpg"
            },
            {
                "cocktail": "Manhattan",
                "cocktail_id": "manhattan",
                "reason": "Rye whisky's spice and sweet vermouth's herbal complexity complement wagyu's deep umami without overpowering it.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Manhattan.jpg"
            },
            {
                "cocktail": "Whisky Highball",
                "cocktail_id": "whisky_highball",
                "reason": "The effervescence cleanses the palate of rich fat between bites — a classic Japanese pairing tradition.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Whisky Highball.jpg"
            }
        ]
    },
    "sashimi": {
        "name": "Sashimi",
        "category": "Seafood",
        "description": "Thinly sliced raw fish of the highest quality — typically salmon, tuna, or yellowtail. Clean, delicate, and oceanic with a silky texture that demands equally clean, refreshing cocktails.",
        "flavour_profile": ["Clean", "Delicate", "Oceanic", "Umami"],
        "video": FOOD_VIDEO_BASE + "sashimi.mp4",
        "pairings": [
            {
                "cocktail": "Martini",
                "cocktail_id": "martini",
                "reason": "The dry, clean botanicals of gin mirror the purity of fresh fish, while cold temperature and salinity echo the oceanic flavour.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Martini.jpg"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "Lime's brightness lifts the delicate fat of raw fish, creating a refreshing contrast that highlights the sashimi's subtle sweetness.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Gimlet.jpg"
            },
            {
                "cocktail": "Whisky Highball",
                "cocktail_id": "whisky_highball",
                "reason": "A traditional Japanese pairing — the light effervescence and gentle whisky notes complement raw fish without masking its flavour.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Whisky Highball.jpg"
            }
        ]
    },
    "tom_yum": {
        "name": "Tom Yum",
        "category": "Soup",
        "description": "Thailand's iconic hot and sour soup, fragrant with lemongrass, kaffir lime, galangal, and chilli. Bold, aromatic, and intensely spiced — it calls for cocktails that cool and refresh.",
        "flavour_profile": ["Spicy", "Sour", "Aromatic", "Herbal"],
        "video": FOOD_VIDEO_BASE + "tom_yum.mp4",
        "pairings": [
            {
                "cocktail": "Mojito",
                "cocktail_id": "mojito",
                "reason": "Fresh mint and lime echo the herbaceous lemongrass and citrus in the soup, while the coolness tames the chilli heat.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "mojito.jpg"
            },
            {
                "cocktail": "Moscow Mule",
                "cocktail_id": "moscow_mule",
                "reason": "Ginger beer's spice harmonises with galangal's warmth, while lime and effervescence cut through the soup's bold aromatics.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Moscow Mule.jpg"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "The sharp citrus-forward profile refreshes the palate between spoonfuls of the intensely flavoured broth.",
                "match_level": "Good",
                "image": COCKTAIL_IMAGE_BASE + "Gimlet.jpg"
            }
        ]
    },
    "truffle_pasta": {
        "name": "Truffle Pasta",
        "category": "Pasta",
        "description": "Fresh pasta enveloped in a luxurious truffle cream sauce — earthy, deeply aromatic, and indulgently rich. The pungent umami of black truffle demands cocktails with complexity and structure.",
        "flavour_profile": ["Earthy", "Rich", "Aromatic", "Creamy"],
        "video": FOOD_VIDEO_BASE + "truffle_pasta.mp4",
        "pairings": [
            {
                "cocktail": "Negroni",
                "cocktail_id": "negroni",
                "reason": "The bitter botanicals of the Negroni cut through the cream's richness, while the sweet vermouth mirrors the earthy depth of truffles.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Negroni.jpg"
            },
            {
                "cocktail": "Manhattan",
                "cocktail_id": "manhattan",
                "reason": "The rye spice and vermouth complexity echo truffle's layered earthiness, creating an elegant high-low contrast.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Manhattan.jpg"
            },
            {
                "cocktail": "Old Fashioned",
                "cocktail_id": "old_fashioned",
                "reason": "Bourbon's vanilla and oak notes harmonise beautifully with truffle's pungent, forest-floor aroma.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Old Fashioned.jpg"
            }
        ]
    },
    "grilled_octopus": {
        "name": "Grilled Octopus",
        "category": "Seafood",
        "description": "Charred, tender octopus with smoky caramelised edges and a clean oceanic sweetness, typically served with citrus, herbs, or a Mediterranean salsa verde.",
        "flavour_profile": ["Smoky", "Oceanic", "Charred", "Tender"],
        "video": FOOD_VIDEO_BASE + "grilled_octopus.mp4",
        "pairings": [
            {
                "cocktail": "Aperol Spritz",
                "cocktail_id": "aperol_spritz",
                "reason": "The bittersweet orange notes of Aperol and the effervescence complement the smoky char and oceanic sweetness of the octopus.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Aperol Spritz.jpg"
            },
            {
                "cocktail": "Paloma",
                "cocktail_id": "paloma",
                "reason": "Grapefruit's tartness cuts through the charred smokiness while complementing the seafood's natural salinity.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Paloma.jpg"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "Crisp lime and gin botanicals echo Mediterranean herbs, cleansing the smoky aftertaste.",
                "match_level": "Good",
                "image": COCKTAIL_IMAGE_BASE + "Gimlet.jpg"
            }
        ]
    },
    "beef_tartare": {
        "name": "Beef Tartare",
        "category": "Meat",
        "description": "Raw, hand-chopped premium beef seasoned with capers, shallots, Dijon mustard, and egg yolk. Bold, briny, and intensely savoury — a dish that commands equally bold cocktails.",
        "flavour_profile": ["Briny", "Savoury", "Bold", "Rich"],
        "video": FOOD_VIDEO_BASE + "beef_tartare.mp4",
        "pairings": [
            {
                "cocktail": "Martini",
                "cocktail_id": "martini",
                "reason": "The clean, cold clarity of a dry Martini echoes the tartare's precise seasoning — both are exercises in elegant restraint.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Martini.jpg"
            },
            {
                "cocktail": "Sazerac",
                "cocktail_id": "sazerac",
                "reason": "The absinthe rinse and rye spice provide a bold counterpoint to the rich raw beef and briny capers.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Sazerac.jpg"
            },
            {
                "cocktail": "Bloody Mary",
                "cocktail_id": "bloody_mary",
                "reason": "The tomato, horseradish, and Worcestershire create a savoury mirror to the tartare's briny umami profile.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Bloody Mary.jpg"
            }
        ]
    },
    "lobster_bisque": {
        "name": "Lobster Bisque",
        "category": "Soup",
        "description": "A velvety, cream-enriched shellfish soup with deep oceanic sweetness, a hint of brandy, and aromatic tarragon. Rich and luxurious — it needs cocktails with enough presence to stand alongside it.",
        "flavour_profile": ["Sweet", "Creamy", "Oceanic", "Luxurious"],
        "video": FOOD_VIDEO_BASE + "lobster_bisque.mp4",
        "pairings": [
            {
                "cocktail": "French 75",
                "cocktail_id": "french_75",
                "reason": "The Champagne and lemon lift the bisque's heavy cream richness, while the gin botanicals complement the lobster's sweetness.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "french_75.jpg"
            },
            {
                "cocktail": "Sidecar",
                "cocktail_id": "sidecar",
                "reason": "Cognac shares the bisque's brandy base, while the orange liqueur and citrus brighten the dish's creamy sweetness.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Sidecar.jpg"
            },
            {
                "cocktail": "Aperol Spritz",
                "cocktail_id": "aperol_spritz",
                "reason": "The light bitterness and effervescence cut through the cream and refresh the palate between spoonfuls.",
                "match_level": "Good",
                "image": COCKTAIL_IMAGE_BASE + "Aperol Spritz.jpg"
            }
        ]
    },
    "foie_gras": {
        "name": "Foie Gras",
        "category": "Delicacy",
        "description": "Silky pan-seared duck liver with an extraordinary buttery richness and subtle sweetness, typically served with brioche and fruit compote. One of the world's most indulgent dishes.",
        "flavour_profile": ["Buttery", "Rich", "Sweet", "Silky"],
        "video": FOOD_VIDEO_BASE + "foie_gras.mp4",
        "pairings": [
            {
                "cocktail": "Sidecar",
                "cocktail_id": "sidecar",
                "reason": "Cognac's stone fruit richness matches foie gras's luxurious fat, while the citrus provides essential acidity to balance the richness.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Sidecar.jpg"
            },
            {
                "cocktail": "French 75",
                "cocktail_id": "french_75",
                "reason": "Champagne's bubbles and acidity cut through the fat with elegance — the classic French pairing for a classic French delicacy.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "french_75.jpg"
            },
            {
                "cocktail": "Vieux Carré",
                "cocktail_id": "vieux_carre",
                "reason": "The Cognac and Benedictine base mirrors the French tradition behind foie gras, adding herbal complexity to the fat.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Vieux Carré.jpg"
            }
        ]
    },
    "spicy_tuna_roll": {
        "name": "Spicy Tuna Roll",
        "category": "Sushi",
        "description": "Fresh tuna mixed with sriracha and sesame oil, rolled in seasoned rice and nori. A balance of oceanic tuna sweetness with a slow-building chilli heat and nutty sesame finish.",
        "flavour_profile": ["Spicy", "Oceanic", "Nutty", "Fresh"],
        "video": FOOD_VIDEO_BASE + "spicy_tuna_roll.mp4",
        "pairings": [
            {
                "cocktail": "Paloma",
                "cocktail_id": "paloma",
                "reason": "Grapefruit's tartness cuts the sriracha heat while complementing the tuna's oceanic sweetness and the sesame's nuttiness.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Paloma.jpg"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "Bright lime and clean gin provide a refreshing cooldown after the chilli heat builds.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Gimlet.jpg"
            },
            {
                "cocktail": "Cucumber Gin Fizz",
                "cocktail_id": "cucumber_gin_fizz",
                "reason": "Cool cucumber and elderflower soothe the spice while echoing the clean, fresh flavours of the roll.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Cucumber Gin Fizz.jpg"
            }
        ]
    },
    "lamb_chops": {
        "name": "Lamb Chops",
        "category": "Meat",
        "description": "Herb-crusted rack of lamb with a rosemary and garlic crust, perfectly pink in the centre. Gamey, rich, and aromatic — a dish that pairs beautifully with bold, complex cocktails.",
        "flavour_profile": ["Gamey", "Herbal", "Rich", "Aromatic"],
        "video": FOOD_VIDEO_BASE + "lamb_chops.mp4",
        "pairings": [
            {
                "cocktail": "Rob Roy",
                "cocktail_id": "rob_roy",
                "reason": "Scotch whisky's peaty earthiness and herbal vermouth mirror the lamb's gamey richness and rosemary crust.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Rob Roy.jpg"
            },
            {
                "cocktail": "Negroni",
                "cocktail_id": "negroni",
                "reason": "Campari's bitter herbal notes contrast the richness of lamb fat beautifully, while the gin botanicals echo the herb crust.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Negroni.jpg"
            },
            {
                "cocktail": "Manhattan",
                "cocktail_id": "manhattan",
                "reason": "The sweet vermouth and whisky structure complement the gamey depth of lamb without overpowering it.",
                "match_level": "Good",
                "image": COCKTAIL_IMAGE_BASE + "Manhattan.jpg"
            }
        ]
    },
    "oysters": {
        "name": "Oysters",
        "category": "Seafood",
        "description": "Fresh raw oysters served on ice with mignonette and lemon — briny, mineral, and oceanic with an incredibly clean finish. One of the most cocktail-friendly foods in existence.",
        "flavour_profile": ["Briny", "Mineral", "Oceanic", "Clean"],
        "video": FOOD_VIDEO_BASE + "oysters.mp4",
        "pairings": [
            {
                "cocktail": "Martini",
                "cocktail_id": "martini",
                "reason": "The definitive oyster pairing. The saline, mineral quality of a cold dry Martini is a direct mirror of the oyster's oceanic brine.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Martini.jpg"
            },
            {
                "cocktail": "French 75",
                "cocktail_id": "french_75",
                "reason": "Champagne's minerality and fine bubbles echo the oyster's ocean brine — a classic French tradition of pairing the two.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "french_75.jpg"
            },
            {
                "cocktail": "Corpse Reviver No. 2",
                "cocktail_id": "corpse_reviver_no2",
                "reason": "The absinthe rinse and Lillet Blanc bring herbal anise notes that pair classically with raw shellfish.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Corpse Reviver No. 2.jpg"
            }
        ]
    },
    "duck_confit": {
        "name": "Duck Confit",
        "category": "Meat",
        "description": "Duck leg slow-cooked in its own fat until the skin is shatteringly crisp and the meat is fall-off-the-bone tender. Rich, deeply savoury, and intensely flavoured.",
        "flavour_profile": ["Rich", "Crispy", "Savoury", "Deep"],
        "video": FOOD_VIDEO_BASE + "duck_confit.mp4",
        "pairings": [
            {
                "cocktail": "Vieux Carré",
                "cocktail_id": "vieux_carre",
                "reason": "The New Orleans classic with Cognac and Benedictine mirrors duck confit's French origins while the rye spice cuts the fat.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Vieux Carré.jpg"
            },
            {
                "cocktail": "Rob Roy",
                "cocktail_id": "rob_roy",
                "reason": "Scotch whisky's smokiness and the herbal vermouth complement the richness of duck fat and crispy skin.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Rob Roy.jpg"
            },
            {
                "cocktail": "Sazerac",
                "cocktail_id": "sazerac",
                "reason": "The absinthe complexity and rye spice cut through duck's intense richness, cleansing the palate between bites.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Sazerac.jpg"
            }
        ]
    },
    "tiramisu": {
        "name": "Tiramisu",
        "category": "Dessert",
        "description": "Italy's iconic layered dessert of espresso-soaked ladyfingers and mascarpone cream, dusted with cocoa. Coffee-forward, gently sweet, and indulgently creamy.",
        "flavour_profile": ["Coffee", "Sweet", "Creamy", "Cocoa"],
        "video": FOOD_VIDEO_BASE + "tiramisu.mp4",
        "pairings": [
            {
                "cocktail": "Espresso Martini",
                "cocktail_id": "espresso_martini",
                "reason": "A natural marriage — the espresso and coffee liqueur in the cocktail directly mirror the dessert's core flavour, amplifying the coffee experience.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "espresso_martini.jpg"
            },
            {
                "cocktail": "White Russian",
                "cocktail_id": "white_russian",
                "reason": "Coffee liqueur and cream echo tiramisu's mascarpone and espresso in liquid form — essentially the same flavour profile.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "White Russian.jpg"
            },
            {
                "cocktail": "Stinger",
                "cocktail_id": "stinger",
                "reason": "The menthol freshness of crème de menthe provides a refreshing contrast to the dense cocoa and cream.",
                "match_level": "Good",
                "image": COCKTAIL_IMAGE_BASE + "Stinger.jpg"
            }
        ]
    },
    "caesar_salad": {
        "name": "Caesar Salad",
        "category": "Salad",
        "description": "Crisp romaine lettuce dressed in an anchovy-rich, garlicky, lemony Caesar dressing with shaved Parmesan and house-made croutons. Bold umami with bright acidity.",
        "flavour_profile": ["Umami", "Tangy", "Savoury", "Crisp"],
        "video": FOOD_VIDEO_BASE + "caesar_salad.mp4",
        "pairings": [
            {
                "cocktail": "Bloody Mary",
                "cocktail_id": "bloody_mary",
                "reason": "The savoury, umami-rich Bloody Mary mirrors the Caesar's anchovy and Worcestershire backbone — both are bold, savoury classics.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Bloody Mary.jpg"
            },
            {
                "cocktail": "Tom Collins",
                "cocktail_id": "tom_collins",
                "reason": "The light, lemony effervescence echoes the salad's citrus dressing and refreshes the palate between bites.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Tom Collins.jpg"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "Lime's brightness complements the tangy Caesar dressing while gin's botanicals echo the herbal Parmesan notes.",
                "match_level": "Good",
                "image": COCKTAIL_IMAGE_BASE + "Gimlet.jpg"
            }
        ]
    },
    "chocolate_lava_cake": {
        "name": "Chocolate Lava Cake",
        "category": "Dessert",
        "description": "Warm dark chocolate fondant with a molten liquid centre that flows when cut — intense, bittersweet, and luxuriously rich. One of the world's most indulgent desserts.",
        "flavour_profile": ["Bittersweet", "Intense", "Rich", "Warm"],
        "video": FOOD_VIDEO_BASE + "chocolate_lava_cake.mp4",
        "pairings": [
            {
                "cocktail": "Oaxacan Old Fashioned",
                "cocktail_id": "oaxacan_old_fashioned",
                "reason": "Mezcal's smoke and the mole bitters create a dark, complex pairing that mirrors the bittersweet chocolate's depth.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Oaxacan Old Fashioned.jpg"
            },
            {
                "cocktail": "Espresso Martini",
                "cocktail_id": "espresso_martini",
                "reason": "Coffee's bitterness amplifies dark chocolate's complexity, while the vodka base keeps it clean and sharp.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "espresso_martini.jpg"
            },
            {
                "cocktail": "Revolver",
                "cocktail_id": "revolver",
                "reason": "The coffee-forward bourbon and Kahlua pair directly with the dark chocolate — warm, sweet, and deeply satisfying.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Revolver.jpg"
            }
        ]
    },
    "pad_thai": {
        "name": "Pad Thai",
        "category": "Noodles",
        "description": "Thailand's beloved stir-fried rice noodles with tamarind, fish sauce, eggs, bean sprouts, and peanuts. Sweet, sour, salty, and savoury in perfect balance with a subtle wok smokiness.",
        "flavour_profile": ["Sweet", "Sour", "Salty", "Nutty"],
        "video": FOOD_VIDEO_BASE + "pad_thai.mp4",
        "pairings": [
            {
                "cocktail": "Singapore Sling",
                "cocktail_id": "singapore_sling",
                "reason": "The tropical fruit sweetness and pineapple juice harmonise with tamarind's sweet-sour profile and peanut's richness.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "singapore_sling.jpg"
            },
            {
                "cocktail": "Mojito",
                "cocktail_id": "mojito",
                "reason": "Mint and lime provide a refreshing, clean contrast to the wok smokiness and fish sauce saltiness.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "mojito.jpg"
            },
            {
                "cocktail": "Paloma",
                "cocktail_id": "paloma",
                "reason": "Grapefruit's bitterness cuts through the noodle dish's richness while the salt rim echoes the dish's seasoning.",
                "match_level": "Good",
                "image": COCKTAIL_IMAGE_BASE + "Paloma.jpg"
            }
        ]
    },
    "burrata": {
        "name": "Burrata",
        "category": "Cheese",
        "description": "Fresh Italian mozzarella filled with stracciatella and cream — extraordinarily milky, soft, and rich. Typically served with heirloom tomatoes, basil, and a drizzle of olive oil.",
        "flavour_profile": ["Milky", "Fresh", "Creamy", "Delicate"],
        "video": FOOD_VIDEO_BASE + "burrata.mp4",
        "pairings": [
            {
                "cocktail": "Aperol Spritz",
                "cocktail_id": "aperol_spritz",
                "reason": "Italy's favourite aperitivo pairs with Italy's favourite starter — the bittersweet orange notes complement the tomato acidity and olive oil.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Aperol Spritz.jpg"
            },
            {
                "cocktail": "Flora",
                "cocktail_id": "flora",
                "reason": "The floral, delicate gin profile and rose water echo burrata's milky freshness and the basil's herbal notes.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Flora.jpg"
            },
            {
                "cocktail": "French 75",
                "cocktail_id": "french_75",
                "reason": "Champagne's acidity and fine bubbles cut the cream's richness elegantly — a light, celebratory pairing.",
                "match_level": "Good",
                "image": COCKTAIL_IMAGE_BASE + "french_75.jpg"
            }
        ]
    },
    "peking_duck": {
        "name": "Peking Duck",
        "category": "Meat",
        "description": "Ceremonial Chinese roasted duck with lacquered, mahogany-crisp skin, served with thin pancakes, hoisin sauce, cucumber, and spring onion. Sweet, smoky, and intensely savoury.",
        "flavour_profile": ["Smoky", "Sweet", "Crispy", "Savoury"],
        "video": FOOD_VIDEO_BASE + "peking_duck.mp4",
        "pairings": [
            {
                "cocktail": "Oaxacan Old Fashioned",
                "cocktail_id": "oaxacan_old_fashioned",
                "reason": "Mezcal's smoke mirrors the duck's lacquered skin, while agave nectar echoes the hoisin sweetness.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Oaxacan Old Fashioned.jpg"
            },
            {
                "cocktail": "Whisky Highball",
                "cocktail_id": "whisky_highball",
                "reason": "A classic East Asian pairing — the light effervescence and mellow whisky wash the palate of the rich duck fat and sweet hoisin.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Whisky Highball.jpg"
            },
            {
                "cocktail": "Dark and Stormy",
                "cocktail_id": "dark_and_stormy",
                "reason": "Dark rum's molasses depth and ginger beer's spice complement the duck's sweet, smoky glaze.",
                "match_level": "Good",
                "image": COCKTAIL_IMAGE_BASE + "Dark and Stormy.jpg"
            }
        ]
    },
    "cheese_board": {
        "name": "Cheese Board",
        "category": "Cheese",
        "description": "A curated selection of artisan cheeses — typically spanning soft brie, aged cheddar, blue cheese, and hard manchego — served with crackers, honey, and fruit.",
        "flavour_profile": ["Varied", "Rich", "Funky", "Complex"],
        "video": FOOD_VIDEO_BASE + "cheese_board.mp4",
        "pairings": [
            {
                "cocktail": "Last Word",
                "cocktail_id": "last_word",
                "reason": "Green Chartreuse's herbal complexity creates a versatile cocktail that finds harmony with every cheese on the board.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Last Word.jpg"
            },
            {
                "cocktail": "Tipperary",
                "cocktail_id": "tipperary",
                "reason": "Irish whiskey and Chartreuse's herbal depth pair particularly well with aged hard cheeses and pungent blues.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "tipperary.jpg"
            },
            {
                "cocktail": "Negroni",
                "cocktail_id": "negroni",
                "reason": "The bitter-sweet-herbal structure of a Negroni is a classic aperitivo pairing for cheese — bitterness cuts through fat and salt.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Negroni.jpg"
            }
        ]
    },
    "ceviche": {
        "name": "Ceviche",
        "category": "Seafood",
        "description": "Fresh raw fish cured in citrus juice — intensely bright, acidic, and fresh with a slight heat from ají amarillo chilli. A Peruvian icon that is clean, vibrant, and punchy.",
        "flavour_profile": ["Acidic", "Bright", "Spicy", "Fresh"],
        "video": FOOD_VIDEO_BASE + "ceviche.mp4",
        "pairings": [
            {
                "cocktail": "Pisco Sour",
                "cocktail_id": "pisco_sour",
                "reason": "The national cocktail of Peru meets the national dish — citrus, pisco, and bitters mirror ceviche's acidity and complexity perfectly.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "pisco_sour.jpg"
            },
            {
                "cocktail": "Paloma",
                "cocktail_id": "paloma",
                "reason": "Grapefruit's sharp citrus amplifies the leche de tigre and cuts through the raw fish with refreshing acidity.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Paloma.jpg"
            },
            {
                "cocktail": "Daiquiri",
                "cocktail_id": "daiquiri",
                "reason": "The lime and rum combination echoes ceviche's citrus cure while the sweetness balances the chilli heat.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "daiquiri.jpg"
            }
        ]
    },
    "grilled_salmon": {
        "name": "Grilled Salmon",
        "category": "Seafood",
        "description": "Salmon fillet with crispy charred skin and a moist, flaky interior — rich in omega oils with a gentle smokiness from the grill and a subtle oceanic sweetness.",
        "flavour_profile": ["Smoky", "Rich", "Oceanic", "Flaky"],
        "video": FOOD_VIDEO_BASE + "grilled_salmon.mp4",
        "pairings": [
            {
                "cocktail": "Elderflower Collins",
                "cocktail_id": "elderflower_collins",
                "reason": "Elderflower's delicate floral sweetness complements the salmon's richness, while lemon and soda cleanse the oiliness.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "elderflower_collins.jpg"
            },
            {
                "cocktail": "Cucumber Gin Fizz",
                "cocktail_id": "cucumber_gin_fizz",
                "reason": "Cool cucumber and gin botanicals provide a fresh, clean contrast to the smoky, fatty salmon.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Cucumber Gin Fizz.jpg"
            },
            {
                "cocktail": "Gimlet",
                "cocktail_id": "gimlet",
                "reason": "Sharp lime and clean gin cut through the rich omega oils and complement the charred grill flavour.",
                "match_level": "Good",
                "image": COCKTAIL_IMAGE_BASE + "Gimlet.jpg"
            }
        ]
    },
    "mushroom_risotto": {
        "name": "Mushroom Risotto",
        "category": "Rice",
        "description": "Slow-stirred Arborio rice with porcini and cremini mushrooms in a rich parmesan-enriched stock. Deeply earthy, umami-laden, and luxuriously creamy with a gentle nuttiness.",
        "flavour_profile": ["Earthy", "Umami", "Creamy", "Nutty"],
        "video": FOOD_VIDEO_BASE + "mushroom_risotto.mp4",
        "pairings": [
            {
                "cocktail": "Toronto",
                "cocktail_id": "toronto",
                "reason": "Fernet-Branca's herbal and earthy bitterness directly complements the porcini's deep forest-floor umami.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "Toronto.jpg"
            },
            {
                "cocktail": "Negroni",
                "cocktail_id": "negroni",
                "reason": "The Negroni's bitter botanical structure cuts through the creamy risotto while sweet vermouth echoes the mushroom's earthiness.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Negroni.jpg"
            },
            {
                "cocktail": "Manhattan",
                "cocktail_id": "manhattan",
                "reason": "Rye whisky's spice and the herbal vermouth create an earthy, warming complement to the mushroom's deep umami.",
                "match_level": "Good",
                "image": COCKTAIL_IMAGE_BASE + "Manhattan.jpg"
            }
        ]
    },
    "tacos_al_pastor": {
        "name": "Tacos Al Pastor",
        "category": "Street Food",
        "description": "Marinated pork cooked on a vertical spit, served in soft corn tortillas with pineapple, cilantro, and onion. Smoky, sweet, citrusy, and boldly spiced.",
        "flavour_profile": ["Smoky", "Sweet", "Spicy", "Citrusy"],
        "video": FOOD_VIDEO_BASE + "tacos_al_pastor.mp4",
        "pairings": [
            {
                "cocktail": "Margarita",
                "cocktail_id": "margarita",
                "reason": "The definitive Mexican pairing — tequila's agave spirit mirrors the al pastor marinade, and the salted rim echoes the taco's seasoning.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "margarita.jpg"
            },
            {
                "cocktail": "Paloma",
                "cocktail_id": "paloma",
                "reason": "Grapefruit's tartness cuts the pork's richness and fat while complementing the pineapple's tropical sweetness.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "Paloma.jpg"
            },
            {
                "cocktail": "Spicy Margarita",
                "cocktail_id": "spicy_margarita",
                "reason": "Jalapeño heat doubles down on the al pastor's chilli spice — for those who love turning up the heat.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "spicy_margarita.jpg"
            }
        ]
    },
    "mango_sticky_rice": {
        "name": "Mango Sticky Rice",
        "category": "Dessert",
        "description": "Thai dessert of sweet glutinous rice cooked in coconut milk, served warm with fresh ripe mango and a drizzle of coconut cream. Sweet, tropical, and fragrant with pandan.",
        "flavour_profile": ["Sweet", "Tropical", "Coconut", "Fragrant"],
        "video": FOOD_VIDEO_BASE + "mango_sticky_rice.mp4",
        "pairings": [
            {
                "cocktail": "Pina Colada",
                "cocktail_id": "pina_colada",
                "reason": "Coconut and pineapple echo the dish's coconut cream and tropical mango, creating a seamless tropical experience.",
                "match_level": "Perfect",
                "image": COCKTAIL_IMAGE_BASE + "pina_colada.jpg"
            },
            {
                "cocktail": "Mango Margarita",
                "cocktail_id": "mango_margarita",
                "reason": "Fresh mango doubled in cocktail form — the tequila's agave sweetness and lime cut the coconut richness.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "mango_margarita.jpg"
            },
            {
                "cocktail": "Mai Tai",
                "cocktail_id": "mai_tai",
                "reason": "The Tiki classic's tropical rum and orgeat create a synergy with the coconut sticky rice's sweet, exotic profile.",
                "match_level": "Excellent",
                "image": COCKTAIL_IMAGE_BASE + "mai_tai.jpg"
            }
        ]
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
#  Mocktail Videos (15 zero-proof drinks)
#  Videos served from: static/mocktail_videos/
# ─────────────────────────────────────────
MOCKTAIL_VIDEO_BASE = "/static/mocktail_videos/"

mocktails = {
    "coffee_limonade": {
        "title": "Coffee Limonade",
        "filename": "COFFEE LIMONADE.mp4",
        "category": "Coffee",
        "description": "A bold and unexpected zero-proof fusion of cold brew coffee and sparkling lemonade — rich coffee depth meets bright citrus for a refreshingly complex sip.",
        "ingredients": ["Cold Brew Coffee", "Lemon Juice", "Simple Syrup", "Sparkling Water", "Lemon Slice"],
        "tags": ["Coffee", "Citrus", "Sparkling", "Bold"],
        "flavour_profile": ["Bold", "Citrusy", "Bittersweet", "Refreshing"],
        "zero_proof": True
    },
    "kiwi_mocktail": {
        "title": "Kiwi Mocktail",
        "filename": "KIWI MOCKTAIL.mp4",
        "category": "Fruit",
        "description": "Freshly muddled kiwi with lime juice and mint, topped with soda — tangy, tropical, and vivid green. A crowd-pleasing zero-proof favourite.",
        "ingredients": ["Fresh Kiwi", "Lime Juice", "Fresh Mint", "Simple Syrup", "Soda Water"],
        "tags": ["Kiwi", "Tropical", "Muddled", "Fruity"],
        "flavour_profile": ["Tangy", "Tropical", "Sweet", "Fresh"],
        "zero_proof": True
    },
    "orange_blue_paradise": {
        "title": "Orange Blue Paradise",
        "filename": "Orange Blue Paradise.mp4",
        "category": "Tropical",
        "description": "A stunning two-tone tropical mocktail layering fresh orange juice over blue curacao syrup — a visual sunset in a glass, sweet and citrusy.",
        "ingredients": ["Orange Juice", "Blue Curacao Syrup", "Lime Juice", "Simple Syrup", "Soda Water"],
        "tags": ["Tropical", "Layered", "Citrus", "Vibrant"],
        "flavour_profile": ["Sweet", "Citrusy", "Tropical", "Vibrant"],
        "zero_proof": True
    },
    "pineapple_ade": {
        "title": "Pineapple Ade",
        "filename": "pineapple_ade.mp4",
        "category": "Tropical",
        "description": "Fresh pineapple juice brightened with lemon and a touch of honey, topped with sparkling water — light, tropical, and effortlessly refreshing.",
        "ingredients": ["Fresh Pineapple Juice", "Lemon Juice", "Honey Syrup", "Sparkling Water", "Pineapple Slice"],
        "tags": ["Pineapple", "Tropical", "Light", "Sparkling"],
        "flavour_profile": ["Tropical", "Sweet", "Bright", "Light"],
        "zero_proof": True
    },
    "blue_lagoon_zero": {
        "title": "Blue Lagoon Zero",
        "filename": "blue_lagoon_zero.mp4",
        "category": "Tropical",
        "description": "A vivid electric-blue zero-proof cooler with blue curacao syrup, lemon juice, and lemonade — visually stunning and refreshingly tropical without any alcohol.",
        "ingredients": ["Blue Curacao Syrup", "Lemon Juice", "Lemonade", "Soda Water"],
        "tags": ["Blue", "Tropical", "Sparkling", "Refreshing"],
        "flavour_profile": ["Tropical", "Sweet", "Citrusy", "Vibrant"],
        "zero_proof": True
    },
    "rose_lychee_refresher": {
        "title": "Rose Lychee Refresher",
        "filename": "Rose Lychee Refresher.mp4",
        "category": "Floral",
        "description": "A delicate and exotic zero-proof blend of lychee juice and rose water with lemon — fragrant, floral, and luxuriously soft on the palate.",
        "ingredients": ["Lychee Juice", "Rose Water", "Lemon Juice", "Simple Syrup", "Sparkling Water"],
        "tags": ["Floral", "Lychee", "Delicate", "Exotic"],
        "flavour_profile": ["Floral", "Sweet", "Delicate", "Exotic"],
        "zero_proof": True
    },
    "mango_chile_limeade": {
        "title": "Mango Chile Limeade",
        "filename": "Mango Chile Limeadeee.mp4",
        "category": "Spicy",
        "description": "Fresh mango purée blended with lime juice and finished with a chilli salt rim — sweet tropical mango with a slow-building fiery kick.",
        "ingredients": ["Mango Puree", "Lime Juice", "Chilli Salt Rim", "Simple Syrup", "Soda Water"],
        "tags": ["Spicy", "Mango", "Tropical", "Bold"],
        "flavour_profile": ["Spicy", "Tropical", "Sour", "Bold"],
        "zero_proof": True
    },
    "passion_fruit_coffee": {
        "title": "Passion Fruit Coffee",
        "filename": "PASSION FRUIT COFFEE.mp4",
        "category": "Coffee",
        "description": "An adventurous zero-proof fusion of cold brew coffee and tangy passion fruit — the bitterness of coffee meets tropical acidity for an unexpected and addictive combination.",
        "ingredients": ["Cold Brew Coffee", "Passion Fruit Puree", "Simple Syrup", "Sparkling Water", "Passion Fruit"],
        "tags": ["Coffee", "Tropical", "Bold", "Unique"],
        "flavour_profile": ["Bold", "Tangy", "Tropical", "Bittersweet"],
        "zero_proof": True
    },
    "virgin_pina_colada": {
        "title": "Virgin Piña Colada",
        "filename": "virgin_pina_colada.mp4",
        "category": "Tropical",
        "description": "Creamy blended coconut cream and fresh pineapple juice over crushed ice — all the sunshine of the Caribbean with zero alcohol.",
        "ingredients": ["Pineapple Juice", "Coconut Cream", "Lime Juice", "Crushed Ice"],
        "tags": ["Tropical", "Creamy", "Blended", "Classic"],
        "flavour_profile": ["Tropical", "Creamy", "Sweet", "Rich"],
        "zero_proof": True
    },
    "hibiscus_lemonade": {
        "title": "Hibiscus Lemonade",
        "filename": "Hibiscus Lemonade.mp4",
        "category": "Floral",
        "description": "A ruby-red zero-proof stunner made from hibiscus flower tea and fresh lemon juice, topped with sparkling water — tart, floral, and visually dramatic.",
        "ingredients": ["Hibiscus Tea", "Lemon Juice", "Honey Syrup", "Sparkling Water", "Lemon Slice"],
        "tags": ["Floral", "Tart", "Vibrant", "Sparkling"],
        "flavour_profile": ["Tart", "Floral", "Fruity", "Vibrant"],
        "zero_proof": True
    },
    "ramos_gin_fizz_zero": {
        "title": "The Ramos Gin Fizz (Zero)",
        "filename": "the Ramos Gin Fizz.mp4",
        "category": "Artisan",
        "description": "A zero-proof take on New Orleans' most legendary drink — non-alcoholic gin, cream, egg white, orange blossom water, and citrus shaken to a cloud-like foam.",
        "ingredients": ["Non-Alcoholic Gin", "Heavy Cream", "Egg White", "Orange Blossom Water", "Lemon Juice", "Lime Juice", "Simple Syrup", "Soda Water"],
        "tags": ["Artisan", "Foam", "Citrus", "New Orleans"],
        "flavour_profile": ["Creamy", "Floral", "Citrusy", "Silky"],
        "zero_proof": True
    },
    "peach_watermelon_cooler": {
        "title": "Peach Watermelon Cooler",
        "filename": "peach watermelon cooler.mp4",
        "category": "Fruit",
        "description": "Freshly blended watermelon and ripe peach with a squeeze of lime and mint — naturally sweet, vibrantly pink, and incredibly cooling.",
        "ingredients": ["Fresh Watermelon Juice", "Peach Puree", "Lime Juice", "Fresh Mint", "Soda Water"],
        "tags": ["Fruity", "Summer", "Pink", "Cooling"],
        "flavour_profile": ["Sweet", "Fruity", "Fresh", "Light"],
        "zero_proof": True
    },
    "lavender_lemonade": {
        "title": "Lavender Lemonade",
        "filename": "avender_lemonade.mp4",
        "category": "Floral",
        "description": "Fragrant lavender syrup stirred with fresh lemon juice and topped with sparkling water — delicately floral, softly sweet, and elegantly purple-hued.",
        "ingredients": ["Lavender Syrup", "Lemon Juice", "Sparkling Water", "Honey", "Lemon Slice"],
        "tags": ["Floral", "Lavender", "Elegant", "Sparkling"],
        "flavour_profile": ["Floral", "Sweet", "Citrusy", "Delicate"],
        "zero_proof": True
    },
    "virgin_mojito": {
        "title": "Virgin Mojito",
        "filename": "virgin_mojito.mp4",
        "category": "Classic",
        "description": "A refreshing alcohol-free take on the Cuban classic — muddled fresh mint and lime with sugar, topped with sparkling water for a lively, cooling effervescence.",
        "ingredients": ["Fresh Mint", "Lime Juice", "Simple Syrup", "Soda Water", "Crushed Ice"],
        "tags": ["Mint", "Citrus", "Muddled", "Classic"],
        "flavour_profile": ["Minty", "Citrusy", "Refreshing", "Light"],
        "zero_proof": True
    }
}

# ─────────────────────────────────────────
#  Garnish Tutorial Videos (11 videos)
#  Videos served from: static/garnish_videos/
# ─────────────────────────────────────────
GARNISH_VIDEO_BASE = "/static/garnish_videos/"

garnish_tutorials = {
    "garnish_orange_peel_01": {
        "title": "Garnish Tutorial 01",
        "filename": "garnish_orange_peel_01.mp4",
        "category": "Garnish",
        "description": "A garnish tutorial video.",
        "tags": ["Garnish", "Tutorial"],
        "difficulty": "Beginner"
    },
    "garnish_orange_peel_02": {
        "title": "Garnish Tutorial 02",
        "filename": "garnish_orange_peel_02.mp4",
        "category": "Garnish",
        "description": "A garnish tutorial video.",
        "tags": ["Garnish", "Tutorial"],
        "difficulty": "Beginner"
    },
    "garnish_orange_twist_03": {
        "title": "Garnish Tutorial 03",
        "filename": "garnish_orange_twist_03.mp4",
        "category": "Garnish",
        "description": "A garnish tutorial video.",
        "tags": ["Garnish", "Tutorial"],
        "difficulty": "Beginner"
    },
    "garnish_orange_twist_04": {
        "title": "Garnish Tutorial 04",
        "filename": "garnish_orange_twist_04.mp4",
        "category": "Garnish",
        "description": "A garnish tutorial video.",
        "tags": ["Garnish", "Tutorial"],
        "difficulty": "Beginner"
    },
    "garnish_orange_carving_05": {
        "title": "Garnish Tutorial 05",
        "filename": "garnish_orange_carving_05.mp4",
        "category": "Garnish",
        "description": "A garnish tutorial video.",
        "tags": ["Garnish", "Tutorial"],
        "difficulty": "Intermediate"
    },
    "garnish_orange_carving_06": {
        "title": "Garnish Tutorial 06",
        "filename": "garnish_orange_carving_06.mp4",
        "category": "Garnish",
        "description": "A garnish tutorial video.",
        "tags": ["Garnish", "Tutorial"],
        "difficulty": "Intermediate"
    },
    "garnish_orange_plate_design_07": {
        "title": "Garnish Tutorial 07",
        "filename": "garnish_orange_plate_design_07.mp4",
        "category": "Garnish",
        "description": "A garnish tutorial video.",
        "tags": ["Garnish", "Tutorial"],
        "difficulty": "Intermediate"
    },
    "garnish_orange_cutting_08": {
        "title": "Garnish Tutorial 08",
        "filename": "garnish_orange_cutting_08.mp4",
        "category": "Garnish",
        "description": "A garnish tutorial video.",
        "tags": ["Garnish", "Tutorial"],
        "difficulty": "Beginner"
    },
    "garnish_orange_knife_skill_09": {
        "title": "Garnish Tutorial 09",
        "filename": "garnish_orange_knife_skill_09.mp4",
        "category": "Garnish",
        "description": "A garnish tutorial video.",
        "tags": ["Garnish", "Tutorial"],
        "difficulty": "Intermediate"
    },
    "garnish_orange_simple_10": {
        "title": "Garnish Tutorial 10",
        "filename": "garnish_orange_simple_10.mp4",
        "category": "Garnish",
        "description": "A garnish tutorial video.",
        "tags": ["Garnish", "Tutorial"],
        "difficulty": "Beginner"
    },
    "garnish_orange_garnish_11": {
        "title": "Garnish Tutorial 11",
        "filename": "garnish_orange_garnish_11.mp4",
        "category": "Garnish",
        "description": "A garnish tutorial video.",
        "tags": ["Garnish", "Tutorial"],
        "difficulty": "Beginner"
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
            "https://assets.mixkit.co/videos/4043/4043-360.mp4",
            "https://assets.mixkit.co/videos/8711/8711-360.mp4"
        ],
        "images": []
    },
    "shaker": {
        "videos": [
            "https://assets.mixkit.co/videos/4174/4174-360.mp4"
        ],
        "images": []
    },
    "pouring": {
        "videos": [
            "https://assets.mixkit.co/videos/4173/4173-360.mp4"
        ],
        "images": []
    },
    "garnish": {
        "videos": [
            "https://assets.mixkit.co/videos/15171/15171-360.mp4"
        ],
        "images": []
    },
    "ambience": {
        "videos": [
            "https://assets.mixkit.co/videos/27819/27819-360.mp4",
            "https://assets.mixkit.co/videos/25458/25458-360.mp4"
        ],
        "images": []
    },
    "glassware": {
        "videos": [
            "https://assets.mixkit.co/videos/22848/22848-360.mp4",
            "https://assets.mixkit.co/videos/22850/22850-360.mp4"
        ],
        "images": []
    },
    "ingredients": {
        "videos": [
            "https://assets.mixkit.co/videos/4295/4295-360.mp4",
            "https://assets.mixkit.co/videos/40487/40487-360.mp4"
        ],
        "images": []
    },
    "cocktail_making": {
        "videos": [
            "https://assets.mixkit.co/videos/43962/43962-360.mp4",
            "https://assets.mixkit.co/videos/4173/4173-360.mp4"
        ],
        "images": []
    }
}


# ─────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────

@app.route("/")
def home():
    return jsonify({
        "message": "🍹 Cocktail API is running!",
        "total_backgrounds": len(background),
        "total_histories": len(cocktail_history),
        "total_pairings": len(food_pairings),
        "total_videos": len(cocktail_videos),
        "total_mocktails": len(mocktails),
        "total_garnish_tutorials": len(garnish_tutorials),
        "endpoints": {
            "GET /api/backgrounds": "Get all background media",
            "GET /api/background/<n>": "Get a specific background by name (e.g. hero, bar, pouring)",
            "GET /api/histories": "Get all cocktail history entries",
            "GET /api/history/<n>": "Get history for a specific cocktail (e.g. negroni, martini)",
            "GET /api/histories/random": "Get a random cocktail history entry",
            "GET /api/pairings": "Get all food pairing entries (supports ?category=)",
            "GET /api/pairing/<n>": "Get cocktail pairings for a specific dish (e.g. wagyu_beef, sashimi)",
            "GET /api/pairings/random": "Get a random food pairing entry",
            "GET /api/pairings/categories": "Get all available food categories",
            "GET /api/videos": "Get all cocktail videos (supports ?category=, ?difficulty=, ?tag=)",
            "GET /api/video/<n>": "Get a specific video entry (e.g. negroni, smoked_old_fashioned)",
            "GET /api/videos/random": "Get a random video entry",
            "GET /api/videos/categories": "Get all video categories",
            "GET /api/mocktails": "Get all mocktail videos (supports ?category=, ?flavour=, ?tag=)",
            "GET /api/mocktail/<n>": "Get a specific mocktail (e.g. virgin_mojito, kiwi_mocktail)",
            "GET /api/mocktails/random": "Get a random mocktail entry",
            "GET /api/mocktails/categories": "Get all mocktail categories",
            "GET /api/garnish_tutorials": "Get all garnish tutorial videos (supports ?difficulty=)",
            "GET /api/garnish_tutorial/<n>": "Get a specific garnish tutorial (e.g. garnish_orange_peel_01)",
            "GET /api/garnish_tutorials/random": "Get a random garnish tutorial"
        }
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


@app.route("/api/history/<name>")
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


@app.route("/api/pairing/<name>")
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
    category_filter   = request.args.get("category",   "").lower()
    difficulty_filter = request.args.get("difficulty", "").lower()
    tag_filter        = request.args.get("tag",        "").lower()

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


@app.route("/api/video/<name>")
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
#  Mocktail Routes
# ─────────────────────────────────────────

def format_mocktail(key, drink):
    return {
        "id": key,
        "title": drink["title"],
        "filename": drink["filename"],
        "url": MOCKTAIL_VIDEO_BASE + drink["filename"],
        "category": drink["category"],
        "description": drink["description"],
        "ingredients": drink["ingredients"],
        "tags": drink["tags"],
        "flavour_profile": drink["flavour_profile"],
        "zero_proof": drink["zero_proof"],
        "total_ingredients": len(drink["ingredients"])
    }


@app.route("/api/mocktails")
def get_all_mocktails():
    category_filter = request.args.get("category", "").lower()
    flavour_filter  = request.args.get("flavour",  "").lower()
    tag_filter      = request.args.get("tag",      "").lower()

    results = []
    for key, drink in mocktails.items():
        if category_filter and category_filter not in drink["category"].lower():
            continue
        if flavour_filter:
            profiles_lower = [f.lower() for f in drink["flavour_profile"]]
            if not any(flavour_filter in f for f in profiles_lower):
                continue
        if tag_filter:
            tags_lower = [t.lower() for t in drink["tags"]]
            if not any(tag_filter in t for t in tags_lower):
                continue
        results.append(format_mocktail(key, drink))

    return jsonify({
        "total": len(results),
        "mocktail_video_base_url": MOCKTAIL_VIDEO_BASE,
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


@app.route("/api/mocktails/categories")
def get_mocktail_categories():
    categories = {}
    for key, drink in mocktails.items():
        cat = drink["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "id": key,
            "title": drink["title"],
            "url": MOCKTAIL_VIDEO_BASE + drink["filename"]
        })
    return jsonify({
        "total_categories": len(categories),
        "categories": categories
    })


# ─────────────────────────────────────────
#  Garnish Tutorial Routes
# ─────────────────────────────────────────

def format_garnish(key, tutorial):
    return {
        "id": key,
        "title": tutorial["title"],
        "filename": tutorial["filename"],
        "url": GARNISH_VIDEO_BASE + tutorial["filename"],
        "category": tutorial["category"],
        "description": tutorial["description"],
        "tags": tutorial["tags"],
        "difficulty": tutorial["difficulty"]
    }


@app.route("/api/garnish_tutorials")
def get_all_garnish_tutorials():
    difficulty_filter = request.args.get("difficulty", "").lower()
    results = []
    for key, tutorial in garnish_tutorials.items():
        if difficulty_filter and difficulty_filter not in tutorial["difficulty"].lower():
            continue
        results.append(format_garnish(key, tutorial))
    return jsonify({
        "total": len(results),
        "garnish_video_base_url": GARNISH_VIDEO_BASE,
        "garnish_tutorials": results
    })


@app.route("/api/garnish_tutorial/<n>")
def get_garnish_tutorial(name):
    key = name.lower().replace(" ", "_").replace("-", "_")
    tutorial = garnish_tutorials.get(key)
    if not tutorial:
        return jsonify({
            "error": f"Garnish tutorial '{name}' not found.",
            "available": list(garnish_tutorials.keys())
        }), 404
    return jsonify(format_garnish(key, tutorial))


@app.route("/api/garnish_tutorials/random")
def get_random_garnish_tutorial():
    key = random.choice(list(garnish_tutorials.keys()))
    return jsonify(format_garnish(key, garnish_tutorials[key]))


# ─────────────────────────────────────────
#  404 fallback
# ─────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found. Visit / for available endpoints."}), 404


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)