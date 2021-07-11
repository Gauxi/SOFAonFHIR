def sofa_coagulation(platelets):
    if platelets is None:
        print('Needed platelets values missing!')
        return 0
    elif platelets < 20:
        return 4
    elif platelets < 50:
        return 3
    elif platelets < 100:
        return 2
    elif platelets < 150:
        return 1
    elif platelets >= 150:
        return 0


def sofa_liver(bilirubin):
    if bilirubin is None:
        print('Needed bilirubin values missing!')
        return 0
    if bilirubin > 12:
        return 4
    elif bilirubin >= 6:
        return 3
    elif bilirubin >= 2:
        return 2
    elif bilirubin >= 1.2:
        return 1
    else:
        return 0


def sofa_kidneys(creatinine, urine):
    if urine is not None:
        if urine < 200:
            return 4
        elif urine < 500:
            return 3

    if creatinine is None:
        print('Needed creatinine values missing!')
        return 0
    elif creatinine > 5:
        return 4
    elif creatinine >= 3.5:
        return 3
    elif creatinine >= 2:
        return 2
    elif creatinine >= 1.2:
        return 1
    else:
        return 0


def sofa_cardio(map, vasopressors):
    if vasopressors['dopamine'] > 15 or vasopressors['adrenaline'] > 0.1 or vasopressors['noradrenaline'] > 0.1:
        return 4
    elif vasopressors['dopamine'] > 5 or 0 < vasopressors['adrenaline'] <= 0.1 or 0 < vasopressors['noradrenaline'] <= 0.1:
        return 3
    elif 0 < vasopressors['dopamine'] <= 5 or vasopressors['dobutamine'] > 0:
        return 2
    elif map is None:
        print('No mean arterial pressure values available!')
        return 0
    elif map < 70:
        return 1
    elif map >= 70:
        return 0


def sofa_respiratory(pao2, fio2, mv):

    if pao2 is None or fio2 is None:
        print('Needed respiratory values missing!')
        return 0
    else:
        pao2_fio2 = pao2 / (fio2/100)

        if pao2_fio2 < 100 and mv == 'confirmed':
            return 4
        elif pao2_fio2 < 200 and mv == 'confirmed':
            return 3
        elif pao2_fio2 < 300:
            return 2
        elif pao2_fio2 < 400:
            return 1
        else:
            return 0


def sofa_gcs(gcs):

    if gcs is None:
        print('Needed Glasgow Coma Scale values missing!')
        return 0
    elif gcs < 6:
        return 4
    elif 6 <= gcs < 10:
        return 3
    elif 10 <= gcs < 13:
        return 2
    elif 12 <= gcs < 15:
        return 1
    elif gcs == 15:
        return 0
