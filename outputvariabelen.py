# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:43:48 2023

@author: Wessel Poorthuis, PBL
"""

output_variabelen_dict = {
                     'Woning' : {
                         'vbo_id' : 'code',
                         },
                     'Adres'  : {
                         'Postcode_huisnummer' :'code',
                          },
                     'Aantal bewoners' : {
                          'Aantal bewoners' : 'aantal',
                          },
                     'Regio' : {
                          'gemeente' : 'code',
                          'wijk'     : 'code',
                          'buurtcode': 'code',
                          },
                     'Woningkenmerken' : {
                          'Kenmerken' : 'code',
                          'woningtype': 'code',
                          'bouwperiode': 'code',
                          'bouwjaar' : 'jaar',
                          'schillabel': 'code',
                          'labeldatum' : 'jaar_maand_dag',
                          'eigendom' : 'code',
                          'oppervlakte' : 'm2',
                          },
                     'Functionele vraag' : {
                          'koken' : 'GJ',
                          'warm tapwater' : 'GJ',
                          'ruimteverwarming' : 'GJ',
                          'Totaal' : 'GJ',
                          'Predictieinterval onderwaarde' : 'GJ',
                          'Predictieinterval bovenwaarde' : 'GJ',
                          'Lokale praktijkfactor' : 'factor',
                          },
                     'Installatietype' : {
                         'installatiecode' : 'code',
                         'Warm tapwater aandeel basis' : 'aandeel',
                         'Ruimteverwarming aandeel basis' : 'aandeel',
                         },
                     'Installatie-efficientie' : {
                         'koken' : 'factor',
                         'warm tapwater basis' : 'factor',
                         'warm tapwater piek' : 'factor',
                         'ruimteverwarming basis' : 'factor',
                         'ruimteverwarming piek' : 'factor',
                         },
                     'Metervraag aardgas' :{
                         'koken' : 'GJ',
                         'warm tapwater basis' : 'GJ',
                         'warm tapwater piek' : 'GJ',
                         'ruimteverwarming basis' : 'GJ',
                         'ruimteverwarming piek' : 'GJ',
                         },
                     'Metervraag elektriciteit' :{
                         'koken' : 'GJ',
                         'warm tapwater basis' : 'GJ',
                         'warm tapwater piek' : 'GJ',
                         'ruimteverwarming basis' : 'GJ',
                         'ruimteverwarming piek' : 'GJ',
                         'hulpvraag' : 'GJ'
                         },
                     'Metervraag warmtenet' :{
                         'warm tapwater basis' : 'GJ',
                         'warm tapwater piek' : 'GJ',
                         'ruimteverwarming basis' : 'GJ',
                         'ruimteverwarming piek' : 'GJ',
                         },
                     'Metervraag waterstof' :{
                         'warm tapwater basis' : 'GJ',
                         'warm tapwater piek' : 'GJ',
                         'ruimteverwarming basis' : 'GJ',
                         'ruimteverwarming piek' : 'GJ',
                         },
                     'Metervraag biomassa' :{
                         'warm tapwater basis' : 'GJ',
                         'warm tapwater piek' : 'GJ',
                         'ruimteverwarming basis' : 'GJ',
                         'ruimteverwarming piek' : 'GJ',
                         },
                     'Metervraag olie' :{
                         'ruimteverwarming basis' : 'GJ',
                         'ruimteverwarming piek' : 'GJ',
                         },
                     'Metervraag totaal' : {
                         'aardgas' : 'GJ',
                         'elektriciteit' : 'GJ',
                         'warmtenet' : 'GJ',
                         'waterstof' : 'GJ',
                         'biomassa' : 'GJ',
                         'olie' : 'GJ',
                         'totaal' : 'GJ',
                         },
                     'Regionale klimaatcorrectie' : {
                         'regionale klimaatcorrectie' : 'factor',
                         }
                     }