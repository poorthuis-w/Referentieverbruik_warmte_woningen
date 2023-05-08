# Referentieverbruik warmte woningen python

Referentieverbruik warmte woningen python can worden gebruikt om de gemeentebestanden uit het project [Referentieverbuik warmte woningen](https://www.pbl.nl/publicaties/referentieverbruik-warmte-woningen#:~:text=Het%20referentieverbruik%20is%20bedoeld%20voor,voor%20particuliere%20eigenaren%20en%20bewoners.) te genereren zonder daarvoor de excel template te gebruiken. 

## Installatie

Clone via github.

## Gebruik

Voeg in de map 'gemeente_inputdata' de databestanden voor de gemeenten toe. Deze zijn te vinden in het [PBL dataportaal referentieverbuik warmte woningen](https://dataportaal.pbl.nl/downloads/VIVET/Referentieverbruik_warmte/). 

In het bestand 'rekenregels.py' is met de variabele 'GM_codes' aan te passen welke gemeente(n) meegenomen worden. Door 'alle_inputdata' in te vullen worden alle databestanden in de map 'gemeente_inputdata' gebruikt. 

Het bestand outputvariabelen.py wordt gebruikt om de structuur van de output dataframe, en daarmee de output .csv, in te stellen. Tevens zijn daar ter referentie de eenehden van de verschillende variabelen te vinden.
## Licentie

[GPL3.0](https://choosealicense.com/licenses/gpl-3.0/)