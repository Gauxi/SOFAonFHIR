import requests
from datetime import datetime

from app.sofaScoreCard import *
from app.unitsOfMeasureCalculator import hour_to_minute, liter_to_dl
from app.helpers import loadCodes
from app import app


headers = app.config['HEADERS']
loinc, snomed = loadCodes()


def calc_total_sofa_score(scores):
    """
    Calculates the SOFA score by summing up all subscores.
    """

    sofa = 0
    for score in scores.values():
        sofa += score
    return sofa


def calc_underscores(patient, source_server):
    """
    Calls functions to calculate each subscore and returns them in a dictionary.
    """

    underscores = {'resp': calc_respiratory(patient,source_server),
                   'ns': calc_gcs(patient, source_server),
                   'cvs': calc_cardio(patient,source_server),
                   'liv': calc_liver(patient, source_server),
                   'coa': calc_coagulation(patient, source_server),
                   'kid': calc_kidneys(patient, source_server)}
    return underscores


def calc_coagulation(patient, source_server):

    patient_platelets = requests.get(url=f'{source_server}/Observation?{patient}&code={loinc}|777-3', headers=headers)
    platelets = patient_platelets.json()

    if 'entry' in platelets:
        platelets_value = platelets['entry'][0]['resource']['valueQuantity']['value']
        platelets_unit = platelets['entry'][0]['resource']['valueQuantity']['unit']
    else:
        platelets_value = None

    return sofa_coagulation(platelets_value)


def calc_cardio(patient, source_server):

    patient_map = requests.get(url=f'{source_server}/Observation?{patient}&code={loinc}|8478-0', headers=headers)
    map = patient_map.json()

    if 'entry' in map:
        map_date = None
        for entry in map['entry']:
            if map_date is None:
                map_date = datetime.strptime(entry['resource']['effectiveDateTime'][:10], '%Y-%m-%d').date()
                map_value = entry['resource']['valueQuantity']['value']
                map_unit = entry['resource']['valueQuantity']['unit']
            elif 'effectiveDateTime' in entry['resource'] and datetime.strptime(entry['resource']['effectiveDateTime'],
                                                                                '%Y-%m-%d').date() > map_date:
                map_date = datetime.strptime(entry['resource']['effectiveDateTime'], '%m-%d-%Y').date()
                map_value = entry['resource']['valueQuantity']['value']
                map_unit = entry['resource']['valueQuantity']['unit']
            elif 'effectivePeriod' in entry['resource'] and datetime.strptime(entry['resource']['effectivePeriod']['end'][:10],
                                                                                '%Y-%m-%d').date() > map_date:
                map_date = datetime.strptime(entry['resource']['effectivePeriod']['end'][:10], '%Y-%m-%d').date()
                map_value = entry['resource']['valueQuantity']['value']
                map_unit = entry['resource']['valueQuantity']['unit']
    else:
        map_value = None

    vasopressors = {}
    patient_dopamine = requests.get(url=f'{source_server}/MedicationStatement?{patient}&code={snomed}|412383006', headers=headers)
    patient_adrenaline = requests.get(url=f'{source_server}/MedicationStatement?{patient}&code={snomed}|387362001', headers=headers)
    patient_noradrenaline = requests.get(url=f'{source_server}/MedicationStatement?{patient}&code={snomed}|45555007', headers=headers)
    patient_dobutamine = requests.get(url=f'{source_server}/MedicationStatement?{patient}&code={snomed}|387145002', headers=headers)
    vasopressors['dopamine'] = patient_dopamine.json()
    vasopressors['adrenaline'] = patient_adrenaline.json()
    vasopressors['noradrenaline'] = patient_noradrenaline.json()
    vasopressors['dobutamine'] = patient_dobutamine.json()

    vasopressors_dose = {}
    for vaso, vaso_values in vasopressors.items():
        if 'entry' in vaso_values:
            vaso_value = vaso_values['entry'][0]['resource']['dosage'][0]['doseAndRate'][0]['rateRatio']['numerator']['value']
            vaso_unit = vaso_values['entry'][0]['resource']['dosage'][0]['doseAndRate'][0]['rateRatio']['numerator']['unit']
            vaso_rate_value = vaso_values['entry'][0]['resource']['dosage'][0]['doseAndRate'][0]['rateRatio']['denominator']['value']
            vaso_rate_unit = vaso_values['entry'][0]['resource']['dosage'][0]['doseAndRate'][0]['rateRatio']['denominator']['unit']

            if vaso_rate_unit == 'hour':
                vaso_rate_value = hour_to_minute(vaso_rate_value)

            vasopressors_dose[vaso] = vaso_value / vaso_rate_value

        else:
            vasopressors_dose[vaso] = 0
    # print('Dopamine: ', vasopressors_dose['dopamine'])
    # print('Dobutamine: ', vasopressors_dose['dobutamine'])
    # print('Adrenaline: ', vasopressors_dose['adrenaline'])
    # print('Noradrenaline: ', vasopressors_dose['noradrenaline'])

    return sofa_cardio(map_value, vasopressors_dose)


def calc_liver(patient, source_server):

    patient_bilirubin = requests.get(url=f'{source_server}/Observation?{patient}&code={loinc}|1974-5', headers=headers)

    bilirubin = patient_bilirubin.json()

    if 'entry' in bilirubin:
        bilirubin_value = bilirubin['entry'][0]['resource']['valueQuantity']['value']
        bilirubin_unit = bilirubin['entry'][0]['resource']['valueQuantity']['unit']
    else:
        bilirubin_value = None

    return sofa_liver(bilirubin_value)


def calc_kidneys(patient, source_server):

    patient_creatinine = requests.get(url=f'{source_server}/Observation?{patient}&code={loinc}|2160-0', headers=headers)

    creatinine = patient_creatinine.json()

    if 'entry' in creatinine:
        creatinine_value = creatinine['entry'][0]['resource']['valueQuantity']['value']
        creatinine_unit = creatinine['entry'][0]['resource']['valueQuantity']['unit']
    else:
        creatinine_value = None

    patient_urine = requests.get(url=f'{source_server}/Observation?{patient}&code={loinc}|3167-4', headers=headers)
    urine = patient_urine.json()

    if 'entry' in urine:
        urine_value = urine['entry'][0]['resource']['valueQuantity']['value']
        urine_unit = urine['entry'][0]['resource']['valueQuantity']['unit']

        if urine_unit == 'L':
            urine_value = liter_to_dl(urine_value)
    else:
        urine_value = None

    return sofa_kidneys(creatinine_value, urine_value)


def calc_respiratory(patient, source_server):

    patient_pao2 = requests.get(url=f'{source_server}/Observation?{patient}&code={loinc}|2019-8', headers=headers)
    pao2 = patient_pao2.json()

    if 'entry' in pao2:
        pao2_value = pao2['entry'][0]['resource']['valueQuantity']['value']
        pao2_unit = pao2['entry'][0]['resource']['valueQuantity']['unit']
    else:
        pao2_value = None

    patient_fio2 = requests.get(url=f'{source_server}/Observation?{patient}&code={loinc}|3150-0', headers=headers)
    fio2 = patient_fio2.json()

    if 'entry' in fio2:
        fio2_value = fio2['entry'][0]['resource']['valueQuantity']['value']
        fio2_unit = fio2['entry'][0]['resource']['valueQuantity']['unit']
    else:
        fio2_value = None

    patient_mv = requests.get(url=f'{source_server}/Condition?{patient}&code={snomed}|444932008', headers=headers)
    mv = patient_mv.json()

    if 'entry' in mv:
        mv_status = mv['entry'][0]['resource']['verificationStatus']['coding'][0]['code']
    else:
        mv_status = None

    return sofa_respiratory(pao2_value, fio2_value, mv_status)


def calc_gcs(patient, source_server):

    patient1_gcs = requests.get(url=f'{source_server}/Observation?{patient}&code={loinc}|9269-2',
                                headers=headers)

    gcs = patient1_gcs.json()

    if 'entry' in gcs:
        gcs_date = None
        for entry in gcs['entry']:
            if gcs_date is None:
                gcs_date = datetime.strptime(entry['resource']['effectiveDateTime'][:10], '%Y-%m-%d').date()
            elif datetime.strptime(entry['resource']['effectiveDateTime'][:10], '%Y-%m-%d').date() > gcs_date:
                gcs_date = datetime.strptime(entry['resource']['effectiveDateTime'][:10], '%Y-%m-%d').date()
            gcs_value = entry['resource']['valueQuantity']['value']
    else:
        gcs_value = None

    return sofa_gcs(gcs_value)

