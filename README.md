# Referentieverbruik warmte woningen python

Referentieverbruik warmte woningen python kan worden gebruikt om de gemeentebestanden uit het project [Referentieverbuik warmte woningen](https://www.pbl.nl/publicaties/referentieverbruik-warmte-woningen#:~:text=Het%20referentieverbruik%20is%20bedoeld%20voor,voor%20particuliere%20eigenaren%20en%20bewoners.) te genereren zonder daarvoor de excel template te gebruiken. Voor meer informatie over de achtergrond en het gebruik van het referentieverbruik warmte woningen, zie het achtergrondrapport, en handleiding en bijsluiter bij het project. 

## Installatie

Het model is via Github binnen te halen. De benodigde mappenstructuur wordt automatisch meegegeven.

Het model gebruikt de packages [numpy](https://numpy.org/) en [pandas](https://pandas.pydata.org/) in de berekeningen. Deze packages zijn daarom vereist in de environment waar het model gedraaid wordt.

## Gebruik

Voeg in de map 'gemeente_inputdata' de databestanden voor de gemeenten toe. Deze zijn te vinden in het [PBL dataportaal referentieverbuik warmte woningen](https://dataportaal.pbl.nl/downloads/VIVET/Referentieverbruik_warmte/). In deze bestanden kunnen aanpassingen worden gedaan als er meer gedetaileerde informatie rondom de energetische kwaliteit van de betreffende woningen beschikbaar is. 

In het bestand 'rekenregels.py' is met de variabele 'GM_codes' aan te passen welke gemeente(n) meegenomen worden. Door 'alle_inputdata' in te vullen worden alle databestanden in de map 'gemeente_inputdata' gebruikt. 

Het bestand outputvariabelen.py wordt gebruikt om de structuur van de output dataframe, en daarmee de output .csv, in te stellen. Tevens zijn daar ter referentie de eenheden van de verschillende variabelen te vinden.

De .csv's in de map datatabellen zijn kentallen overgenomen uit de gemeentebestanden. Deze waarden worden gebruikt in de rekenregels om de uitkomsten van de gemeentebestande  te reproduceren.

## Licentie

[GPL3.0](https://choosealicense.com/licenses/gpl-3.0/)

## Contact

Schroom niet contact op te nemen voor vragen en suggesties.

Wessel Poorthuis

wessel.poorthuis@pbl.nl

Planbureau voor de Leefomgeving
