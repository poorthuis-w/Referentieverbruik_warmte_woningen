# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 09:15:33 2023

@author: Wessel Poorthuis, PBL
"""
# Reset parameters tussen python runs in Spyder
from IPython import get_ipython
get_ipython().run_line_magic('reset', '-sf')
#%%
# Import modules
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
import pandas as pd
import numpy as np
import glob
import time
import re

from outputvariabelen import output_variabelen_dict

def inlezen_gemeentedata(path, GM_codes):
    '''
    Leest gemeentedatabestanden in als dataframe. 
    '''
    
    if GM_codes == ['alle_inputdata']:
        gemeentedata_path = os.path.join(path,'gemeente_inputdata', '*.csv')

        gemeente_files = glob.glob(gemeentedata_path)
        input_file = gemeente_files[0]
        kolommen = pd.read_csv(input_file, sep=',').columns
        df = pd.DataFrame(columns=kolommen)
        
        for gemeentebestand in gemeente_files:
            df_gemeente = pd.read_csv(gemeentebestand, sep=',') 
            df = pd.concat([df, df_gemeente])
    else:
        input_file = f'Data_{GM_codes[0]}.csv'
        kolommen = pd.read_csv(os.path.join(path, 'gemeente_inputdata', input_file), sep=',').columns
        df = pd.DataFrame(columns=kolommen)
        
        for gemeente_code in GM_codes:
            input_file = f'Data_{gemeente_code}.csv'
            df_gemeente = pd.read_csv(os.path.join(path, 'gemeente_inputdata', input_file), sep=',') 
            df = pd.concat([df, df_gemeente])
    
    return df

def datavoorbereiding_niet_ingevulde_velden(df_in):
    '''
    Geeft dummywaarden aan onbekende woningkenmerken
    '''
    
    df_in['W'].fillna(9999, inplace=True)
    df_in['B'].fillna(9999, inplace=True)
    df_in['E'].fillna(9999, inplace=True)
    df_in['bouwjaar'].fillna(9999, inplace=True)
    
    
    return df_in

def inlezen_brondata(path):
    '''
    Leest csv's met brondata in als dataframes en zet deze in een dictionary
    '''
    brondata_dict = {}
    brondata_path = os.path.join(path, 'datatabellen', '*.csv')
    brondatabestanden_list = glob.glob(brondata_path)
    
    for brondatabestand in brondatabestanden_list:
        naam = maak_dict_naam(brondatabestand)
        df = pd.read_csv(os.path.join(brondata_path, brondatabestand), sep=';') 
        brondata_dict[naam] = df
    
    return brondata_dict

def maak_dict_naam(volledige_locatie_string):
    '''
    Maakt behapbare names voor brondata brondata_dict
    '''
    dict_naam = os.path.split(volledige_locatie_string)[1]
    dict_naam = os.path.splitext(dict_naam)[0]
    
    return dict_naam

def definieer_constanten():
    '''
    Definieert enkele constanten en zet deze in dictionary
    '''
    constanten_dict = {
    'onderwaarde_energieinhoud_aardgas_m3_naar_GJ'            : 0.03165,
    'vermogen_kW_op_een_kwart_van_functionele_vraag_GJ'       : 0.25,
    'vermogen_installatie_warm_tapwater_eengezinswoning_KW'   : 4,
    'vermogen_installatie_warm_tapwater_meergezinswoning_KW'  : 2,
    'standaard_jaarverbruik_correctie'                        : 0.918979578314703,
    'bandbreedte_aangevulde_waarden_m3_aardgas'               : 1500
    }
    
    return constanten_dict

def instantieer_output_dataframe(output_variabelen):
    '''
    Maakt output dataframe op basis van outoputvariabelen in outputvariabelen.py
    '''
    df = pd.DataFrame(columns = output_variabelen)
    
    return df
    
def overnemen_basisdata(df_input, df_output):
    '''
    Zet data direct over van gemeenteinput naar gemeenteoutput
    '''
    df_output['Woning/vbo_id']               = df_input['BAG_id']
    df_output['Adres/Postcode_huisnummer']   = df_input['adres']
    df_output['Regio/gemeente']              = df_input['BU_CODE'].str.slice(start=3, stop=7)
    df_output['Regio/wijk']                  = df_input['BU_CODE'].str.slice(start=3, stop=9)
    df_output['Regio/buurtcode']             = df_input['BU_CODE']
    df_output['Woningkenmerken/Kenmerken']   = df_input['TBE_string']
    df_output['Woningkenmerken/woningtype']  = df_input['W'].astype(int)
    df_output['Woningkenmerken/bouwperiode'] = df_input['B'].astype(int)
    df_output['Woningkenmerken/bouwjaar']    = df_input['bouwjaar'].astype(int)
    df_output['Woningkenmerken/schillabel']  = df_input['energielabel']
    df_output['Woningkenmerken/labeldatum']  = df_input['labeldatum']
    df_output['Woningkenmerken/eigendom']    = df_input['E'].astype(int)
    df_output['Woningkenmerken/oppervlakte'] = df_input['Oppervlak [m^2]'].astype(int)

    df_output['Functionele vraag/Lokale praktijkfactor'] = df_input['lokale praktijkfactor']
    df_output['Regionale klimaatcorrectie/regionale klimaatcorrectie'] = df_input['klimaatfactor']
        
    return df_output

def bereken_functionele_vraag(df_output, benodigde_woningkenmerken):
    '''
    Geeft structuur voor het berekenen van de functionele vraag
    '''
    df_output['Aantal bewoners/Aantal bewoners']    = bereken_huishoudgrootte(df_output.loc[:,benodigde_woningkenmerken], brondata_dict['Kentallen_aantal_bewoners_populatie_1a_1b'], brondata_dict['Kentallen_aantal_bewoners_populatie_2'])
    df_output['Functionele vraag/koken']            = bereken_functionele_vraag_koken(df_output.loc[:,benodigde_woningkenmerken], brondata_dict['Kentallen_koken'])
    df_output['Functionele vraag/warm tapwater']    = bereken_functionele_vraag_warm_tapwater(df_output.loc[:,benodigde_woningkenmerken], brondata_dict['Kentallen_warm_tapwater'])
    df_output['Functionele vraag/ruimteverwarming'] = bereken_functionele_vraag_ruimteverwarming(df_output.loc[:,benodigde_woningkenmerken], brondata_dict['Kentallen_ruimteverwarming_populatie_1a'], brondata_dict['Kentallen_ruimteverwarming_populatie_1b'], brondata_dict['Kentallen_ruimteverwarming_populatie_2'])
    df_output['Functionele vraag/Totaal']           = df_output['Functionele vraag/koken'] + df_output['Functionele vraag/warm tapwater'] + df_output['Functionele vraag/ruimteverwarming']  
    df_output = functionele_vraag_bij_datagebrek(df_output)
    # Predictieinterval is een todo

    return df_output

def functionele_vraag_bij_datagebrek(df_output):
    '''
    Plaatst NaN waarden bij functionele vraag als woningtype niet bekend is.
    '''
    woningen_met_onbekende_woningkenmerken = df_output['Woningkenmerken/woningtype'] == 9999
    df_output.loc[woningen_met_onbekende_woningkenmerken,'Functionele vraag/koken'] = float("nan")
    df_output.loc[woningen_met_onbekende_woningkenmerken,'Functionele vraag/warm tapwater'] = float("nan")
    df_output.loc[woningen_met_onbekende_woningkenmerken,'Functionele vraag/ruimteverwarming'] = float("nan")
    df_output.loc[woningen_met_onbekende_woningkenmerken,'Functionele vraag/Totaal'] = 0

    return df_output

def bereken_huishoudgrootte(df_output, datatabel_1, datatabel_2):
    '''
    Berekent huishoudgrootte op basis van woningtype, bouwperiode, eigendom, schillabel (indien beschikbaar) en oppervlakte.
    '''

    datatabel_1.rename(columns={'W' : 'Woningkenmerken/woningtype', 'B' : 'Woningkenmerken/bouwperiode', 'E' : 'Woningkenmerken/eigendom', 'S' : 'Woningkenmerken/schillabel', 'RE_OA_a' : 'RE_OA_a_1', 'RE_OA_b' : 'RE_OA_b_1'}, inplace=True)
    datatabel_2.rename(columns={'W' : 'Woningkenmerken/woningtype', 'B' : 'Woningkenmerken/bouwperiode', 'E' : 'Woningkenmerken/eigendom',                                     'RE_OA_a' : 'RE_OA_a_2', 'RE_OA_b' : 'RE_OA_b_2'}, inplace=True)
    
    res = df_output.merge(datatabel_1, how='left', on=['Woningkenmerken/woningtype', 'Woningkenmerken/bouwperiode', 'Woningkenmerken/eigendom', 'Woningkenmerken/schillabel'])
    res =       res.merge(datatabel_2, how='left', on=['Woningkenmerken/woningtype', 'Woningkenmerken/bouwperiode', 'Woningkenmerken/eigendom'                              ])
    huishoudgrootte_1 = res['Woningkenmerken/oppervlakte'] * res['RE_OA_a_1'] + res['RE_OA_b_1']
    huishoudgrootte_2 = res['Woningkenmerken/oppervlakte'] * res['RE_OA_a_2'] + res['RE_OA_b_2']
    
    res['Huishoudgrootte'] = huishoudgrootte_1
    res['Huishoudgrootte'] = res['Huishoudgrootte'].fillna(huishoudgrootte_2)
    res['Huishoudgrootte'] = res['Huishoudgrootte'].round(0)
    
    return res['Huishoudgrootte']

def bereken_functionele_vraag_koken(df_output, datatabel_koken):
    '''
    Berekent functionele vraag naar koken op basis van bouwperiode, oppervlakte en aantal inwoners.
    '''
    df_output['TNO_bouwjaarklasse_code']    = categoriseer_bouwjaarklasse_TNO(df_output['Woningkenmerken/bouwjaar'])
    df_output['TNO_oppervlakteklasse_code'] = categoriseer_oppervlakteklasse_TNO(df_output['Woningkenmerken/oppervlakte'])

    SPF_gasfornuis = brondata_dict['Aannames_installaties_voor_koken'].loc[0, 'SPF']

    res = df_output.merge(datatabel_koken, how='left', left_on=['TNO_bouwjaarklasse_code', 'TNO_oppervlakteklasse_code', 'Aantal bewoners/Aantal bewoners'], right_on=['Bouwjaarklasse code', 'Oppervlakteklasse TNO code', 'Huishoudgrootte'])

    res['functionele vraag koken'] = res['Gecorrigeerd gasgebruik koken [m3]'] * constanten_dict['onderwaarde_energieinhoud_aardgas_m3_naar_GJ'] * SPF_gasfornuis
    res['functionele vraag koken'] = res['functionele vraag koken'] * res['Functionele vraag/Lokale praktijkfactor']
    
    return res['functionele vraag koken']

def bereken_functionele_vraag_warm_tapwater(df_output, datatabel_tapwater):
    '''
    Berekent functionele vraag naar warm tapwater op basis van oppervlakte en aantal inwoners.
    '''
    
    df_output['TNO_oppervlakteklasse_code'] = categoriseer_oppervlakteklasse_TNO(df_output['Woningkenmerken/oppervlakte'])

    SPF_b_Hr = brondata_dict['Aannames_installaties_voor_warm_tapwater'].at[11, 'SPF_b']
    SPF_p_Hr = brondata_dict['Aannames_installaties_voor_warm_tapwater'].at[11, 'SPF_p']
    P_vol_Hr = brondata_dict['Aannames_installaties_voor_warm_tapwater'].at[11, 'P_vol']

    res = df_output.merge(datatabel_tapwater, how='left', left_on=['TNO_oppervlakteklasse_code', 'Aantal bewoners/Aantal bewoners'], right_on=['Oppervlakteklasse TNO code', 'Gezinsgrootte'])
    
    res['functionele vraag tapwater basis'] = res['gasverbruik warm water (m3)'] * constanten_dict['onderwaarde_energieinhoud_aardgas_m3_naar_GJ'] * P_vol_Hr * SPF_b_Hr
    res['functionele vraag tapwater piek'] = res['gasverbruik warm water (m3)'] * constanten_dict['onderwaarde_energieinhoud_aardgas_m3_naar_GJ'] * (1-P_vol_Hr) * SPF_p_Hr

    res['functionele vraag tapwater'] = res['functionele vraag tapwater basis']  + res['functionele vraag tapwater piek']
    res['functionele vraag tapwater'] = res['functionele vraag tapwater'] * res['Functionele vraag/Lokale praktijkfactor']
    
    return res['functionele vraag tapwater']

def bereken_functionele_vraag_ruimteverwarming(df_output, datatabel_1a, datatabel_1b, datatabel_2):
    '''
    Berekent functionele vraag naar warm tapwater op basis van oppervlakte en aantal inwoners.
    '''
    
    df_output_vrijstaand_met_label    = df_output[(df_output['Woningkenmerken/woningtype'] == 1) & (df_output['Woningkenmerken/schillabel'] != 'x')]
    df_output_vrijstaand_zonder_label = df_output[(df_output['Woningkenmerken/woningtype'] == 1) & (df_output['Woningkenmerken/schillabel'] == 'x')]
    df_output_overig_met_label        = df_output[(df_output['Woningkenmerken/woningtype'] != 1) & (df_output['Woningkenmerken/schillabel'] != 'x')]
    df_output_overig_zonder_label     = df_output[(df_output['Woningkenmerken/woningtype'] != 1) & (df_output['Woningkenmerken/schillabel'] == 'x')]
    df_output_zonder_label = pd.concat([df_output_vrijstaand_zonder_label,df_output_overig_zonder_label]).sort_index()

    res_vrijstaand_met_label = df_output_vrijstaand_met_label.merge(datatabel_1b, how='left', left_on=['Woningkenmerken/woningtype', 'Woningkenmerken/bouwperiode', 'Woningkenmerken/eigendom', 'Woningkenmerken/schillabel'], right_on=['W', 'B', 'E', 'S'])
    res_overig_met_label     = df_output_overig_met_label.merge(    datatabel_1a, how='left', left_on=['Woningkenmerken/woningtype', 'Woningkenmerken/bouwperiode', 'Woningkenmerken/eigendom', 'Woningkenmerken/schillabel'], right_on=['W', 'B', 'E', 'S'])
    res_zonder_label         = df_output_zonder_label.merge(        datatabel_2,  how='left', left_on=['Woningkenmerken/woningtype', 'Woningkenmerken/bouwperiode', 'Woningkenmerken/eigendom'], right_on=['W', 'B', 'E'])

    res_vrijstaand_met_label['functionele vraag ruimteverwarming'] = res_vrijstaand_met_label['Woningkenmerken/oppervlakte'] * res_vrijstaand_met_label['RE_FO_a_WBE [m3 aardgas]'] + res_vrijstaand_met_label['RE_FO_b_WBSE [m3 aardgas]']
    res_overig_met_label['functionele vraag ruimteverwarming']     = res_overig_met_label['Woningkenmerken/oppervlakte'] * res_overig_met_label['RE_FO_a_WBE [m3 aardgas]'] + res_overig_met_label['RE_FO_b_WBSE [m3 aardgas]']
    res_zonder_label['functionele vraag ruimteverwarming']         = res_zonder_label['Woningkenmerken/oppervlakte'] * res_zonder_label['RE_FO_a_WBE [m3 aardgas]'] + res_zonder_label['RE_FO_b_WBE [m3 aardgas]']
    res = pd.concat([res_vrijstaand_met_label, res_overig_met_label, res_zonder_label], ignore_index=True)
    res = res.loc[:,['Woning/vbo_id', 'functionele vraag ruimteverwarming']]
    df_output = df_output.merge(res, how='left', on=['Woning/vbo_id'])

    df_output['functionele vraag ruimteverwarming'] = df_output['functionele vraag ruimteverwarming'] * df_output['Functionele vraag/Lokale praktijkfactor'] * df_output['Regionale klimaatcorrectie/regionale klimaatcorrectie'] * constanten_dict['onderwaarde_energieinhoud_aardgas_m3_naar_GJ']

    return df_output['functionele vraag ruimteverwarming']

def categoriseer_bouwjaarklasse_TNO(bouwjaar):
    '''
    Categoriseert bouwjaar naar TNO bouwjaarklasse.
    '''
    conditions = [
        (bouwjaar <= 1930),
        (bouwjaar > 1930) & (bouwjaar <= 1959),
        (bouwjaar > 1959) & (bouwjaar <= 1980),
        (bouwjaar > 1980) & (bouwjaar <= 1995),
        (bouwjaar > 1995)
        ]
    values = [0,1,2,3,4]
    TNO_bouwjaarklasse_code = np.select(conditions, values)

    return TNO_bouwjaarklasse_code

def categoriseer_oppervlakteklasse_TNO(oppervlakte):
    '''
    Categoriseert oppervlakte naar TNO oppervlakteklasse.
    '''
    conditions = [
        (oppervlakte <= 75),
        (oppervlakte >  75) & (oppervlakte <= 100),
        (oppervlakte > 100) & (oppervlakte <= 125),
        (oppervlakte > 125) & (oppervlakte <= 150),
        (oppervlakte > 150)
        ]
    values = [1,2,3,4,5]
    TNO_oppervlakteklasse_code = np.select(conditions, values)

    return TNO_oppervlakteklasse_code

def bepaal_installatiecode(df_gemeentedata, datatabel):
    '''
   Bepaalt installatiecode op basis van opgegeven installaties in invoerbestand.
    '''
    res = df_gemeentedata.merge(datatabel, how='left', left_on=['Inst_RVb', 'Inst_RVp', 'Inst_TWb', 'Inst_TWp', 'Koken'], right_on=['ruimteverwarming (basis)', 'ruimteverwarming (piek)', 'warm tapwater(basis)', 'warm tapwater (piek)', 'koken'])
        
    return res.loc[:, 'code']



def bepaal_installatie_parameters(df_output, datatabel_installatiecodes, datatabel_ruimteverwarming, datatabel_warm_tapwater, datatabel_koken):
    '''
    Maakt dataframe met installatieparameters
    '''
    variabelen_TW_RV = ['Installatie_name', 'AS_Name', 'Input_name', 'P_vol', 'P_cap', 'SPF_b', 'SPF_p', 'eEffect_cap', 'schillabel_name']
    variabelen_KK    = ['Installatie_name', 'Input_name', 'SPF']
    installaties = df_output.merge(datatabel_installatiecodes, how='left', left_on ='Installatietype/installatiecode', right_on='code')

    installaties = ophalen_installatie_parameters_datatabellen(installaties, datatabel_warm_tapwater.loc[:, variabelen_TW_RV], 'warm tapwater(basis)', 'TW_b')
    installaties = ophalen_installatie_parameters_datatabellen(installaties, datatabel_warm_tapwater.loc[:, variabelen_TW_RV], 'warm tapwater (piek)', 'TW_p')

    installaties = ophalen_installatie_parameters_datatabellen(installaties, datatabel_ruimteverwarming.loc[:, variabelen_TW_RV], 'ruimteverwarming (basis)', 'RV_b')
    installaties = ophalen_installatie_parameters_datatabellen(installaties, datatabel_ruimteverwarming.loc[:, variabelen_TW_RV], 'ruimteverwarming (piek)', 'RV_p')

    installaties = ophalen_installatie_parameters_datatabellen(installaties, datatabel_koken.loc[:,variabelen_KK], 'koken', 'KK')

    installaties.drop(list(installaties.filter(regex = 'Installatie')), axis = 1, inplace = True)
    installaties.drop(list(installaties.filter(regex = 'schillabel')), axis = 1, inplace = True)

    return installaties

def ophalen_installatie_parameters_datatabellen(installaties, datatabel, installatie, functie):
    '''
    Haalt voor alle woningen de parameters behorend bij de installaties voor ruimteverwarwarming (RV), warm tapwater (TW) en koken (KK) op.
    '''
    if 'RV' in functie:
        datatabel = datatabel.add_suffix(f'_{functie}')
        installaties = installaties.merge(datatabel, how='left', left_on= [installatie, 'Woningkenmerken/schillabel'], right_on=[f'Installatie_name_{functie}', f'schillabel_name_{functie}'], suffixes=('', '_y'))
        installaties_nan = installaties.copy()
        installaties_nan.loc[:,'Woningkenmerken/schillabel'] = 'x'
        installaties_nan = installaties_nan.merge(datatabel, how='left', left_on= [installatie, 'Woningkenmerken/schillabel'], right_on=[f'Installatie_name_{functie}', f'schillabel_name_{functie}'], suffixes=('_nonnan', ''))
        installaties.fillna(installaties_nan, inplace=True)
        installaties.drop(f'schillabel_name_{functie}', axis=1, inplace=True)
    else:
        datatabel = datatabel.add_suffix(f'_{functie}')
        installaties = installaties.merge(datatabel, left_on= installatie, right_on=f'Installatie_name_{functie}', suffixes=('', '_y'))

    installaties.drop(installaties.filter(regex='_y$').columns, axis=1, inplace=True)
    
    return installaties

def bereken_metervragen(df_output, installatie_parameters):
    '''
    Geeft de structuur voor het berekenen van de metervragen voor de verschillende functies en voegt de berekende metervragen in bij df_output
    '''
    # Koken
    benodigde_variabelen_df_output_koken = ['Woning/vbo_id','Functionele vraag/koken']
    benodigde_variabelen_installatie_parameters_koken = ['Woning/vbo_id','SPF_KK', 'Input_name_KK']
    df_input_metervraag_koken = df_output[benodigde_variabelen_df_output_koken].merge(installatie_parameters[benodigde_variabelen_installatie_parameters_koken], on='Woning/vbo_id')
    metervragen_koken = bereken_metervraag_koken(df_input_metervraag_koken)
    df_output = merge_metervraag_in_df_ouput(df_output, metervragen_koken)

    # Warm tapwater
    benodigde_variabelen_df_output_warm_tapwater = ['Woning/vbo_id','Functionele vraag/warm tapwater']
    benodigde_variabelen_installatie_parameters_warm_tapwater = ['Woning/vbo_id','SPF_b_TW_b', 'SPF_p_TW_p', 'P_vol_TW_b', 'Input_name_TW_b','Input_name_TW_p']
    df_input_metervraag_warm_tapwater = df_output[benodigde_variabelen_df_output_warm_tapwater].merge(installatie_parameters[benodigde_variabelen_installatie_parameters_warm_tapwater], on='Woning/vbo_id')
    metervragen_warm_tapwater = bereken_metervraag_warm_tapwater(df_input_metervraag_warm_tapwater)
    df_output = merge_metervraag_in_df_ouput(df_output, metervragen_warm_tapwater)

    # Ruimteverwarming
    benodigde_variabelen_df_output_ruimteverwarming = ['Woning/vbo_id','Functionele vraag/ruimteverwarming']
    benodigde_variabelen_installatie_parameters_ruimteverwarming = ['Woning/vbo_id','SPF_b_RV_b', 'SPF_p_RV_p', 'P_vol_RV_b', 'Input_name_RV_b','Input_name_RV_p']
    df_input_metervraag_ruimteverwarming = df_output[benodigde_variabelen_df_output_ruimteverwarming].merge(installatie_parameters[benodigde_variabelen_installatie_parameters_ruimteverwarming], on='Woning/vbo_id')
    metervragen_ruimteverwarming = bereken_metervraag_ruimteverwarming(df_input_metervraag_ruimteverwarming)
    df_output = merge_metervraag_in_df_ouput(df_output, metervragen_ruimteverwarming)
    
    # Hulpenergie
    benodigde_variabelen_df_output_hulpenergie = ['Woning/vbo_id', 'Woningkenmerken/woningtype', 'Functionele vraag/ruimteverwarming']
    benodigde_variabelen_installatie_parameters_hulpenergie = ['Woning/vbo_id', 'P_cap_TW_b', 'P_cap_RV_b', 'eEffect_cap_TW_b','eEffect_cap_TW_p','eEffect_cap_RV_b','eEffect_cap_RV_p']
    df_input_metervraag_hulpenergie = df_output[benodigde_variabelen_df_output_hulpenergie].merge(installatie_parameters[benodigde_variabelen_installatie_parameters_hulpenergie], on='Woning/vbo_id')
    metervraag_hulpenergie = bereken_metervraag_hulpenergie(df_input_metervraag_hulpenergie)
    df_output = merge_metervraag_in_df_ouput(df_output, metervraag_hulpenergie)
    
    return df_output

def bereken_metervraag_koken(df_input):
    '''        
    Berekent de metervraag naar koken voor alle relevante energiedragers
    '''        
    metervraag_koken = pd.DataFrame()
    metervraag_koken['Woning/vbo_id'] = df_input['Woning/vbo_id']
    
    metervraag = df_input['Functionele vraag/koken'] / df_input['SPF_KK']
    
    conditions = ['gas', 'elektriciteit']
    values     = ['aardgas', 'elektriciteit']
    
    for val, cond in enumerate(conditions):
        metervraag_koken.loc[df_input['Input_name_KK'] == cond, f'Metervraag {values[val]}/koken'] = metervraag
        
    metervraag_koken.fillna(0, inplace=True)

    return metervraag_koken

def bereken_metervraag_warm_tapwater(df_input):
    '''        
    Berekent de metervraag naar warm tapwater voor alle relevante energiedragers
    '''        
    metervraag_warm_tapwater = pd.DataFrame()
    metervraag_warm_tapwater['Woning/vbo_id'] = df_input['Woning/vbo_id']

    metervraag_basis = df_input['Functionele vraag/warm tapwater'] / df_input['SPF_b_TW_b'] * df_input['P_vol_TW_b']
    metervraag_piek  = df_input['Functionele vraag/warm tapwater'] / df_input['SPF_p_TW_p'] * (1-df_input['P_vol_TW_b'])
    
    conditions = [    'gas', 'elektriciteit',      'geen', 'waterstof', 'biomassa']
    values     = ['aardgas', 'elektriciteit', 'warmtenet', 'waterstof', 'biomassa']
    
    for val, cond in enumerate(conditions):
        metervraag_warm_tapwater.loc[df_input['Input_name_TW_b'] == cond, f'Metervraag {values[val]}/warm tapwater basis'] = metervraag_basis
        metervraag_warm_tapwater.loc[df_input['Input_name_TW_p'] == cond, f'Metervraag {values[val]}/warm tapwater piek'] = metervraag_piek
        
    metervraag_warm_tapwater.fillna(0, inplace=True)

    return metervraag_warm_tapwater

def bereken_metervraag_ruimteverwarming(df_input):
    '''        
    Berekent de metervraag naar ruimteverwarming voor alle relevante energiedragers
    '''        
    metervraag_ruimteverwarming = pd.DataFrame()
    metervraag_ruimteverwarming['Woning/vbo_id'] = df_input['Woning/vbo_id']
    
    metervraag_basis = df_input['Functionele vraag/ruimteverwarming'] / df_input['SPF_b_RV_b'] * df_input['P_vol_RV_b']
    metervraag_piek  = df_input['Functionele vraag/ruimteverwarming'] / df_input['SPF_p_RV_p'] * (1-df_input['P_vol_RV_b'])
    
    conditions = [    'gas', 'elektriciteit',      'geen', 'waterstof', 'biomassa', 'olie']
    values     = ['aardgas', 'elektriciteit', 'warmtenet', 'waterstof', 'biomassa', 'olie']

    for val, cond in enumerate(conditions):
        metervraag_ruimteverwarming.loc[df_input['Input_name_RV_b'] == cond, f'Metervraag {values[val]}/ruimteverwarming basis'] = metervraag_basis
        metervraag_ruimteverwarming.loc[df_input['Input_name_RV_p'] == cond, f'Metervraag {values[val]}/ruimteverwarming piek'] = metervraag_piek
        
    metervraag_ruimteverwarming.fillna(0, inplace=True)
    
    return metervraag_ruimteverwarming

def bereken_metervraag_hulpenergie(df_input):
    '''        
    Berekent hulpvraag obv functinele vraag naar ruimteverwarming, woningtype (eengezins/meergezins) en installaties voor ruimteverwarming en warm tapwater.
    Op het moment wordt voor iedere woning zowel de meergezisn als de eengezinshulpvraag voor warm tapwater berekend. Een effciencyslag is om dit selectiever te doen.
    '''        
    metervraag_hulpenergie = pd.DataFrame()
    metervraag_hulpenergie['Woning/vbo_id'] = df_input['Woning/vbo_id']
    metervraag_hulpenergie['Woningkenmerken/woningtype'] = df_input['Woningkenmerken/woningtype']
    
    hulpenergie_ruimteverwarming_basis = df_input['Functionele vraag/ruimteverwarming'] * constanten_dict['vermogen_kW_op_een_kwart_van_functionele_vraag_GJ'] * df_input['P_cap_RV_b'] * df_input['eEffect_cap_RV_b']
    hulpenergie_ruimteverwarming_piek = df_input['Functionele vraag/ruimteverwarming'] * constanten_dict['vermogen_kW_op_een_kwart_van_functionele_vraag_GJ'] * (1-df_input['P_cap_RV_b']) * df_input['eEffect_cap_RV_p']
    
    hulpenergie_warm_tapwater_basis_eengezins = constanten_dict['vermogen_installatie_warm_tapwater_eengezinswoning_KW'] *  df_input['P_cap_TW_b'] * df_input['eEffect_cap_TW_b']
    hulpenergie_warm_tapwater_piek_eengezins = constanten_dict['vermogen_installatie_warm_tapwater_eengezinswoning_KW'] *  (1-df_input['P_cap_TW_b']) * df_input['eEffect_cap_TW_p']
    
    hulpenergie_warm_tapwater_basis_meergezins = constanten_dict['vermogen_installatie_warm_tapwater_meergezinswoning_KW'] *  df_input['P_cap_TW_b'] * df_input['eEffect_cap_TW_b']
    hulpenergie_warm_tapwater_piek_meergezins = constanten_dict['vermogen_installatie_warm_tapwater_meergezinswoning_KW'] *  (1-df_input['P_cap_TW_b']) * df_input['eEffect_cap_TW_p']
    
    eengezins_list = [1,2,3,4]
    metervraag_hulpenergie.loc[metervraag_hulpenergie['Woningkenmerken/woningtype'].isin(eengezins_list), 'Metervraag elektriciteit/hulpvraag'] = hulpenergie_ruimteverwarming_basis + hulpenergie_ruimteverwarming_piek + hulpenergie_warm_tapwater_basis_eengezins + hulpenergie_warm_tapwater_piek_eengezins
    metervraag_hulpenergie.loc[~metervraag_hulpenergie['Woningkenmerken/woningtype'].isin(eengezins_list), 'Metervraag elektriciteit/hulpvraag'] = hulpenergie_ruimteverwarming_basis + hulpenergie_ruimteverwarming_piek + hulpenergie_warm_tapwater_basis_meergezins + hulpenergie_warm_tapwater_piek_meergezins

    return metervraag_hulpenergie

def merge_metervraag_in_df_ouput(df_output, metervraag):
    '''        
    Zet uitkomsten van berekening metervragen op juiste plek in df_output ipv achteraan
    '''        
    df_output = df_output.merge(metervraag, how='left', on='Woning/vbo_id', suffixes=('', '_y'))
    for col in metervraag:
        if 'vbo' not in col:
           df_output[col] = df_output[f'{col}'].fillna(df_output[f'{col}_y'])
           df_output.astype({f'{col}' : 'float64'})
    df_output.drop(df_output.filter(regex='_y$').columns, axis=1, inplace=True)
    
    return df_output

def bereken_metervraag_totalen(df_output):
    '''
    Berekent metervraagtotalen per energiedrager en voor alle energiedragers samengenomen
    '''
    energiedragers     = ['aardgas', 'elektriciteit', 'warmtenet', 'waterstof', 'biomassa', 'olie']

    
    for drager in energiedragers:
        df_output.loc[:,f'Metervraag totaal/{drager}'] = df_output.loc[:,df_output.columns.str.contains(f'Metervraag {drager}')].sum(axis=1)
        
    df_output.loc[:,'Metervraag totaal/totaal'] = df_output.loc[:,df_output.columns.str.contains('Metervraag totaal')].sum(axis=1)

    return df_output

def invoegen_installatie_parameters(df_output, installatie_parameters):
    '''
    Voegt bepaalde installatieparameters toe aan df_output
    '''
    
    df_output = df_output.merge(installatie_parameters, how='left', on='Woning/vbo_id', suffixes=('', '_y'))
    for col in installatie_parameters:
        if 'vbo' not in col:
            df_output[col] = df_output[f'{col}'].fillna(df_output[f'{col}_y'])
            df_output.astype({f'{col}' : 'float64'})
    df_output.drop(df_output.filter(regex='_y$').columns, axis=1, inplace=True)
    
    return df_output

def downcast(df):
    '''
    Downcasten van variabelen om grootte dataset te verkleinen voor wegschrijven
    https://towardsdatascience.com/how-to-reduce-the-size-of-a-pandas-dataframe-in-python-7ed6e4269f88
    '''
    for column in df:
        if df[column].dtype == 'float64':
            df[column]=pd.to_numeric(df[column], downcast='float')
        if df[column].dtype == 'int64':
            df[column]=pd.to_numeric(df[column], downcast='integer')

    return df

def wegschrijven_naar_csv(df_output, path, GM_code):
    '''
    Doet laatste aanpassing nodig voor wegschrijven en schrijft daaran df_output weg als .csv 
    '''
    output_path = os.path.join(path,'output')
    outputfolder_exists = os.path.exists(output_path)

    if outputfolder_exists == False:
        os.makedirs(output_path)

    if behoud_nullen_excel_parameter == True:
        df_output = behoud_leading_zeroes_excel(df_output)
    
    if wegschrijven_per_gemeente_parameter == True:
        wegschrijven_per_gemeente(df_output, output_path)
    else:
        wegschrijven_in_een_bestand(df_output, output_path, GM_code)

def afronden_voor_output(df_output, aantal_decimalen_af_te_ronden):
    '''
    Rondt kolommen met functionele vraag, metervraag en de regionale klimaatcorrectie af. 
    '''
    kolommen_af_te_ronden_list = ['Functionele vraag', 'Metervraag', 'klimaatcorrectie']
    kolommen_af_te_ronden_pattern = '|'.join(kolommen_af_te_ronden_list)
    kolommen_af_te_ronden = df_output.filter(regex=kolommen_af_te_ronden_pattern).columns

    for col in kolommen_af_te_ronden:    
        df_output.loc[:, col] = df_output.astype({f'{col}' : 'float64'})
        
    kolommen_af_te_ronden = kolommen_af_te_ronden.drop(labels=['Functionele vraag/Lokale praktijkfactor','Regionale klimaatcorrectie/regionale klimaatcorrectie'])

    if type(aantal_decimalen_af_te_ronden) == int:
        df_output[kolommen_af_te_ronden] = df_output[kolommen_af_te_ronden].round(aantal_decimalen_af_te_ronden)
    
    return df_output

def behoud_leading_zeroes_excel(df_output):
    '''
    Zorgt er voor dat in Excel de eerste nullen bij de wijk en buurtcodes niet verwdijnen.
    '''
    df_output['Regio/gemeente'] = df_output['Regio/gemeente'].apply('="{}"'.format)
    df_output['Regio/wijk'] = df_output['Regio/wijk'].apply('="{}"'.format)
    
    return df_output

def wegschrijven_per_gemeente(df_output, output_path):
    '''
    Maakt voor iedere gemeente een aparte csv  met output.
    '''
    for gemeentecode in df_output['Regio/gemeente'].unique():
        df_gemeente = df_output[df_output['Regio/gemeente'] == gemeentecode].copy()
        
        if behoud_nullen_excel_parameter == False:
            gemeentecode_name = gemeentecode
        elif behoud_nullen_excel_parameter == True:
            gemeentecode_name = int(re.findall(r'\d+', gemeentecode)[0])
        gemeentecode_name = str(gemeentecode_name).zfill(4)

        df_gemeente.to_csv(os.path.join(output_path, f'GM{gemeentecode_name}.csv'), sep=';', chunksize=100000)
  
def wegschrijven_in_een_bestand(df_output, output_path, GM_code):
    '''
    Schrijft output dataframe weg naar een enkel .csv bestand.
    '''
    gemeentecode_name = '_'.join(GM_code)
    
    df_output.to_csv(os.path.join(output_path, f'{gemeentecode_name}.csv'), sep=';', chunksize=100000)


def get_keys(dictionary):
    '''
    Maakt lijst met strings van nested dictionary
    Bron: https://gist.github.com/PatrikHlobil/9d045e43fe44df2d5fd8b570f9fd78cc
    '''
    result = []
    for key, value in dictionary.items():
        if type(value) is dict:
            new_keys = get_keys(value)
            #result.append(key)
            for innerkey in new_keys:
                result.append(f'{key}/{innerkey}')
        else:
            result.append(key)
            
    return result    
#%%
if __name__ == "__main__":
    start_time = time.time()
    
    path = os.getcwd()
    GM_codes = ['GM0088'] # Mogelijkheid tot opgeven meerdere gemeentecodes in lijst. gebruik ['alle_inputdata'] voor alle gemeentes in inputadata map.
    decimalen_af_te_ronden = 2 # Geeft aan op hoe veel decimalen de functionele en metervragen worden afgerond. Als er geen getal staat wordt er niet afgerond
    behoud_nullen_excel_parameter = False # Wanneer excel de output inleest verwdijnen de leading zeros bij de gemeentedoce en de wijkcode. Met deze parameter blijven deze behouden, al maken ze de csv voor andere toepassingen minder bruikbaar.
    wegschrijven_per_gemeente_parameter = False # Wanneer True wordt voor iedere gemeente een aparte output .csv gemaakt. Als False, dan alle output in een .csv
    
    # Inlezen data
    df_gemeentedata_input = inlezen_gemeentedata(path, GM_codes)
    brondata_dict         = inlezen_brondata(path)
    
    df_gemeentedata_input = datavoorbereiding_niet_ingevulde_velden(df_gemeentedata_input)
    constanten_dict       = definieer_constanten()
    data_ingelezen_time = time.time()
    print('Data ingelezen. Tijdsduur:', round(data_ingelezen_time - start_time,2) ,'s')
    
    # Instantieren output dataframe
    output_columns_list = get_keys(output_variabelen_dict)
    df_output = instantieer_output_dataframe(output_columns_list)
    df_output = overnemen_basisdata(df_gemeentedata_input, df_output)
    df_output['Installatietype/installatiecode'] = bepaal_installatiecode(df_gemeentedata_input, brondata_dict['Aannames_installatiecodes_met_bijbehorende_installatietypen'])
    del df_gemeentedata_input

    # Functionele vraag
    benodigde_woningkenmerken_functionele_vraag = ['Woning/vbo_id', 'Woningkenmerken/oppervlakte','Woningkenmerken/woningtype', 'Woningkenmerken/bouwperiode', 'Woningkenmerken/bouwjaar', 'Woningkenmerken/eigendom', 'Woningkenmerken/schillabel', 'Aantal bewoners/Aantal bewoners', 'Functionele vraag/Lokale praktijkfactor', 'Regionale klimaatcorrectie/regionale klimaatcorrectie']
    df_output = bereken_functionele_vraag(df_output, benodigde_woningkenmerken_functionele_vraag)
    functionele_vraag_berekend_time = time.time()
    print('Functionele vraag berekend. Tijdsduur:', round(functionele_vraag_berekend_time - data_ingelezen_time,2) ,'s')

    # Installaties
    benodigde_woningkenmerken_installaties = ['Woning/vbo_id','Installatietype/installatiecode','Woningkenmerken/schillabel']
    installatie_parameters = bepaal_installatie_parameters(df_output[benodigde_woningkenmerken_installaties], brondata_dict['Aannames_installatiecodes_met_bijbehorende_installatietypen'], brondata_dict['Aannames_installaties_voor_ruimteverwarming'], brondata_dict['Aannames_installaties_voor_warm_tapwater'], brondata_dict['Aannames_installaties_voor_koken'])

    # Metervragen
    df_output = bereken_metervragen(df_output, installatie_parameters)    
    df_output = bereken_metervraag_totalen(df_output)
    metervraag_berekend_time = time.time()
    print('Metervragen berekend. Tijdsduur:', round(metervraag_berekend_time - functionele_vraag_berekend_time,2) ,'s')
    
    # Invoegen installatieparameters
    installatieparameters_hernoeming_dict = {'Woning/vbo_id' : 'Woning/vbo_id',
                                            'P_vol_TW_b'    : 'Installatietype/Warm tapwater aandeel basis',
                                            'P_vol_RV_b'    : 'Installatietype/Ruimteverwarming aandeel basis',
                                            'SPF_KK'        : 'Installatie-efficientie/koken',
                                            'SPF_b_TW_b'    : 'Installatie-efficientie/warm tapwater basis',
                                            'SPF_p_TW_p'    : 'Installatie-efficientie/warm tapwater piek',
                                            'SPF_b_RV_b'    : 'Installatie-efficientie/ruimteverwarming basis',
                                            'SPF_p_RV_p'    : 'Installatie-efficientie/ruimteverwarming piek'}
    df_output = invoegen_installatie_parameters(df_output, installatie_parameters[installatieparameters_hernoeming_dict.keys()].rename(columns=installatieparameters_hernoeming_dict))
    #%%
    # Klaar maken voor output en wegschrijven naar csv
    df_output = afronden_voor_output(df_output, decimalen_af_te_ronden)
    df_output = downcast(df_output)
    wegschrijven_naar_csv(df_output, path, GM_codes)
    einde_time = time.time()
    print('Data weggeschreven. Tijdsduur:', round(einde_time - metervraag_berekend_time,2) ,'s')
    print('Eind script. Totale Tijdsduur:', round(einde_time - start_time,2) ,'s')
