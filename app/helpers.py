from app import app


def loadServers():
    source_server = app.config['SOURCE_SERVER']
    target_server = app.config['TARGET_SERVER']
    return source_server, target_server

def loadCodes():
    loinc = app.config['CODES']['loinc']
    snomed = app.config['CODES']['snomed']
    return loinc, snomed