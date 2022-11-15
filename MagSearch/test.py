import yaml

with open('stopwords.yml') as f:
    stopwords = yaml.load(f, yaml.SafeLoader)
d = stopwords['stopwords']['NL']
l = d.split(',')
r = [e.strip() for e in l]

# stopwords = ['aan', 'acht', 'achter', 'achteren', 'afhankelijk', 'alle', 'alleen', 'allemaal', \
#  'alles', 'als', 'alsnog', 'altijd', 'andere', 'anders', 'beetje', 'behalve', 'behoorlijk', \
#  'behulp', 'beide', 'believen', 'best', 'bestaan', 'bestaat', 'betekent', 'beter', 'betreft', \
#  'bevat', 'bevinden', 'bieden', 'biedt', 'bij', 'bijna', 'bijvoorbeeld', 'binnen', 'blijft', \
#  'blijkbaar', 'blijven', 'bouwt', 'boven', 'bovenaan', 'buiten', 'circa', 'daar', 'daarbij', 'daarentegen', \
#  'daarmee', 'daarna', 'daarom', 'daarop', 'daartoe', 'daarvan', 'daarvoor', 'dan', 'dankzij', \
#  'danwel', 'dat', 'de', 'denkt', 'derde', 'dergelijk', 'dergelijke', 'desondanks', 'deze', 'dezelfde', \
#  'die', 'dik', 'dikkere', 'direct', 'direkt', 'dit', 'doen', 'doet', 'door', 'doorgaans', \
#  'draaien', 'draait', 'drie', 'dringend', 'dus', 'echt', 'echter', 'een', 'eens', 'eenvoudig', \
#  'eerder', 'eerst', 'eerste', 'eigen', 'eigenlijk', 'elk', 'elkaar', 'elke', 'enige', 'enkele', 'eraan', \
#  'erg', 'erin', 'ermee', 'eruit', 'ervoor', 'evenals', 'extra', 'figuur', 'gaan', 'gaat', \
#  'gaf', 'gebeurd', 'gebeurde', 'gebeuren', 'gebeurt', 'gebruik', 'gebruiken', 'gebruikt', \
#  'gedraaid', 'geeft', 'geen', 'gegeven', 'gehad', 'geheel', 'geholpen', 'gehouden', 'gelegen', \
#  'gemaakt', 'gemeten', 'genoeg', 'genomen', 'geschikt', 'geschreven', 'geval', 'geven', 'gewoon', \
#  'goed', 'goede', 'gratis', 'groot', 'grote', 'grotere', 'haalt', 'had', 'heb', 'hebben', \
#  'hebt', 'heeft', 'heel', 'helaas', 'hele', 'helpen', 'helpt', 'hen', 'het', 'hetzelfde', \
#  'hier', 'hierin', 'hiermee', 'hiervan', 'hiervoor', 'hij', 'hoe', 'hoewel', 'hoge', 'hoog', \
#  'hou', 'houd', 'houden', 'houdt', 'hun', 'ieder', 'iedere', 'iets', 'indien', 'is', 'juist', \
#  'juiste', 'kan', 'kant', 'kijken', 'kijker', 'klaar', 'klein', 'kleine', 'komen', 'komt', \
#  'kort', 'korte', 'krijgen', 'kun', 'kunnen', 'kunt', 'laag', 'laat', 'lang', 'langer', 'laten', \
#  'later', 'liefst', 'liggen', 'ligt', 'lijken', 'lijkt', 'links', 'maak', 'maakt', 'maar', \
#  'mag', 'maken', 'makkelijk', 'manier', 'mee', 'meer', 'meest', 'meestal', 'meeste', 'meet', \
#  'men', 'met', 'meteen', 'meten', 'midden', 'mij', 'mijn', 'min', 'minder', 'minst', 'minstens', \
#  'misschien', 'moest', 'moet', 'moeten', 'mogelijk', 'mogen', 'na', 'naar', 'naarmate', 'naast', \
#  'nadat', 'nagenoeg', 'natuurlijk', 'nauwelijks', 'nee', 'neemt', 'negen', 'nemen', 'nergens', \
#  'niet', 'nodig', 'nog', 'nogmaals', 'nooit', 'nou', 'nu', 'ofwel', 'omdat', 'omvat', 'onder', \
#  'onderaan', 'ongeveer', 'ons', 'onze', 'ooit', 'ook', 'opeenvolgende', 'opnieuw', 'over', 'overigens', \
#  'paar', 'pas', 'per', 'plus', 'prettig', 'qua', 'recent', 'recente', 'rechts', 'rond', 'schikt', \
#  'schreef', 'schrijven', 'sla', 'slaan', 'slaat', 'slecht', 'slechts', 'snelle', 'soepel', 'sommige', \
#  'soms', 'soort', 'staan', 'start', 'steeds', 'stevig', 'stop', 'stuk', 'tegen', 'telkens', \
#  'ten', 'tenslotte', 'ter', 'terug', 'terwijl', 'tevens', 'tien', 'toch', 'toe', 'toen', \
#  'tonen', 'toonde', 'toont', 'tot', 'tussen', 'twee', 'tweede', 'uit', 'uiteraard', 'uitgebreid', \
#  'uitvoeren', 'vaak', 'van', 'vanaf', 'vanuit', 'vast', 'vasthouden', 'vastzetten', 'veel', 'verder', \
#  'verdere', 'verscheidene', 'vervolgens', 'via', 'vier', 'vijf', 'vind', 'vinden', 'vindt', \
#  'vlot', 'vlotte', 'voeren', 'volgende', 'volgens', 'volledig', 'voor', 'vooraf', 'vooral', \
#  'voordat', 'vrij', 'vrijwel', 'vroeger', 'waar', 'waarbij', 'waardoor', 'waarmee', 'waarna', \
#  'waarom', 'waaronder', 'waarop', 'waarschijnlijk', 'waaruit', 'waarvan', 'wanneer', 'want', \
#  'was', 'wat', 'weer', 'weg', 'wegens', 'weinig', 'wel', 'weliswaar', 'welk', 'welke', 'wellicht', \
#  'werd', 'werkelijk', 'werken', 'werkt', 'wie', 'wil', 'willen', 'wilt', 'worden', 'wordt', \
#  'www', 'zal', 'zeer', 'zeker', 'zelden', 'zelf', 'zelfs', 'zes', 'zeven', 'zich', 'zie', \
#  'zien', 'ziet', 'zijn', 'zit', 'zitten', 'zoals', 'zodat', 'zodoende', 'zodra', 'zogenaamd', \
#  'zogenaamde', 'zolang', 'zonder', 'zou', 'zouden', 'zoveel', 'zowel', 'zozeer', 'zulke', 'zullen']
# 
# sw = sorted(stopwords)
# 
# f = open('stopwords.txt', 'w')
# s = '    '
# for w in sw:
#     s = s + w + ', '
#     if len(s) > 80:
#         f.write(s+'\n')
#         s = '    '
# f.write(s[:-2]+'\n')
# f.close()
