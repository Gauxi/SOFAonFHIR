class Config(object):
    DEBUG = True
    ENVIRONMENT = 'DEVELOPMENT'
    DEFAULT_ORGANISATION = '1234'
    SOURCE_SERVER = 'http://localhost:8080'
    TARGET_SERVER = 'http://localhost:8080'

    HEADERS = {
                "Accept": "application/fhir+json; fhirVersion=4.0",
                "Content-Type": "application/fhir+json; fhirVersion=4.0",
            }

    CODES = {
                "loinc": "http://loinc.org",
                "snomed": "http://snomed.info/sct"
            }
