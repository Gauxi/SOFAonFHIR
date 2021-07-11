import json
import uuid
from datetime import date
import datetime

import requests
from fhirclient.models import (meta, procedure, observation, patient, codeableconcept, coding, fhirdate, fhirreference, device, bundle as bdl)


def createSofaResources(patient_id, org_id, sofa_underscores, sofa_score, source_server, target_server, headers,
                        create_new_patient):
    """
    Creates and post requests the SOFA Observation with the SOFA Score, the SOFA Procedure as the act of calculating the
    SOFA Score and the SOFA Device as reference of the here used software. The Resources will be packed into a FHIR
    Bundle. If the server does not accept the bundle, they will be send each separately. They are also locally saved.

    :return: dictionary
        status code of response requests
    """

    # Generates IDs for the Resources and adds the ones for the patient and organisation
    ids = {'obs_id': uuid.uuid4(), 'prod_id': uuid.uuid4(), 'dev_id': uuid.uuid4(), 'pat_id': patient_id, 'org_id': org_id}
    sofa_observation = createSofaObservation(ids, sofa_underscores, sofa_score)
    sofa_procedure = createSofaProcedure(ids)
    sofa_device = createSofaDevice(ids)

    # Fallback if a patient is not yet created on the target server
    if create_new_patient:
        new_patient_id = createNewPatient(ids, source_server, target_server, headers)
        sofa_observation, sofa_procedure = setNewReferences(new_patient_id, sofa_observation, sofa_procedure)
    else:
        new_patient_id = None

    resources = [sofa_observation, sofa_procedure, sofa_device]

    # Dictonary to collect status responses of posted Resources
    status = {}

    # Bundles the resources and asks the target server for a post validation
    sofa_bundle = createBundle(resources)
    response = requests.post(f'{target_server}/$validate', headers=headers, data=json.dumps(sofa_bundle.as_json()))
    bundle_status = response.status_code
    status['bundle_status'] = bundle_status

    # If the target server validated the request, the bundle will be posted to the server
    if bundle_status == 200:
        req = requests.post(f'{target_server}', headers=headers, data=json.dumps(sofa_bundle.as_json()))
        bundle_status = req.status_code
        status["bundle_status"] = bundle_status

        # Additionally saves the Bundle Resource locally
        fname = 'Bundle-SOFA-' + str(ids['pat_id']) + '.json'
        with open('data/' + fname, 'w') as outfile:
            json.dump(sofa_bundle.as_json(), outfile, indent=4)

    # If Bundle request was not validated or successfully created, the Resources will be posted separately
    if bundle_status != 200 and bundle_status != 201:

        # Checked validation
        # response = requests.post(f'{target_server}$validate', headers=headers, data=json.dumps(sofa_observation.as_json()))
        # print(response.json())
        # response = requests.post(f'{target_server}$validate', headers=headers, data=json.dumps(sofa_procedure.as_json()))
        # print(response.json())
        # response = requests.post(f'{target_server}$validate', headers=headers, data=json.dumps(sofa_device.as_json()))
        # print(response.json())

        req = requests.post(f'{target_server}', headers=headers, data=json.dumps(sofa_observation.as_json()))
        status["obs_status"] = req.status_code
        fname = 'Observation-SOFA-' + str(ids['pat_id']) + '.json'
        with open('data/' + fname, 'w') as outfile:
            json.dump(sofa_observation.as_json(), outfile, indent=4)

        # Saving of a response Resource
        # fname = 'Response-Observation-SOFA-' + str(ids['pat_id']) + '.json'
        # with open('data/' + fname, 'w') as outfile:
        #     json.dump(req.json(), outfile, indent=4)

        req = requests.post(f'{target_server}', headers=headers, data=json.dumps(sofa_procedure.as_json()))
        status["prod_status"] = req.status_code
        fname = 'Procedure-SOFA-' + str(ids['pat_id']) + '.json'
        with open('data/' + fname, 'w') as outfile:
            json.dump(sofa_procedure.as_json(), outfile, indent=4)

        req = requests.post(f'{target_server}', headers=headers, data=json.dumps(sofa_device.as_json()))
        status["dev_status"] = req.status_code
        fname = 'Device-SOFA-' + str(ids['pat_id']) + '.json'
        with open('data/' + fname, 'w') as outfile:
            json.dump(sofa_device.as_json(), outfile, indent=4)

    return status, new_patient_id


def createBundle(resources):

    dateTime = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
    dateTime = str(dateTime)

    bundle_entries = []

    for resource in resources:
        full_url = 'urn:uuid:' + str(resource.identifier[0].value)
        if resource.resource_type in ['Patient', 'Procedure', 'Device']:
            req_method = 'PUT'
            req_url = str(resource.resource_type) + '/' + str(resource.identifier[0].value)
        else:
            req_method = 'POST'
            req_url = str(resource.resource_type)

        request = bdl.BundleEntryRequest()
        request.method = req_method
        request.url = req_url

        entry = bdl.BundleEntry()
        entry.request = request
        entry.resource = resource
        entry.fullUrl = full_url

        bundle_entries.append(entry)

    sofa_bundle = bdl.Bundle()
    sofa_bundle.type = "transaction"
    # YYYY-MM-DDThh:mm:ss.sss+zz:zz
    sofa_bundle.timestamp = fhirdate.FHIRDate(dateTime)
    sofa_bundle.entry = bundle_entries

    return sofa_bundle


def createSofaObservation(ids, sofa_underscores, sofa_score):

    sofa_observation = observation.Observation()

    identifier = observation.identifier.Identifier()
    identifier.system = f'https://fhir/hospital/{ids["org_id"]}'
    identifier.value = str(ids['obs_id'])
    sofa_observation.identifier = [identifier]

    sofa_observation.id = str(ids['obs_id'])

    sofa_meta = meta.Meta()
    sofa_meta.profile = ['https://www.netzwerk-universitaetsmedizin.de/fhir/StructureDefinition/sofa-score']
    sofa_observation.meta = sofa_meta

    partOf = fhirreference.FHIRReference()
    partOf.reference = f'Procedure/{ids["prod_id"]}'
    sofa_observation.partOf = [partOf]

    status = 'final'
    sofa_observation.status = status

    category = codeableconcept.CodeableConcept()
    assessment_category = coding.Coding()
    assessment_category.system = 'http://terminology.hl7.org/CodeSystem/observation-category'
    assessment_category.code = 'survey'
    category.coding = [assessment_category]
    sofa_observation.category = [category]

    code = codeableconcept.CodeableConcept()
    assessment_coding = coding.Coding()
    assessment_coding.system = 'https://www.netzwerk-universitaetsmedizin.de/fhir/CodeSystem/ecrf-parameter-codes'
    assessment_coding.code = '06'
    code.coding = [assessment_coding]
    sofa_observation.code = code

    subject = fhirreference.FHIRReference()
    subject.reference = f'Patient/{ids["pat_id"]}'
    sofa_observation.subject = subject

    fhir_date = fhirdate.FHIRDate(str(date.today()))
    sofa_observation.effectiveDateTime = fhir_date

    value = sofa_score
    sofa_observation.valueInteger = value

    method = codeableconcept.CodeableConcept()
    assessment_method = coding.Coding()
    assessment_method.system = 'http://snomed.info/sct'
    assessment_method.code = '459231000124102'
    method.coding = [assessment_method]
    sofa_observation.method = method

    device = fhirreference.FHIRReference()
    device.reference = f'Device/{ids["dev_id"]}'
    sofa_observation.device = device

    # Adding the subscores
    components = ['resp', 'ns', 'cvs', 'liv', 'coa', 'kid']
    list_of_sofa_components = []

    for component in components:

        sofa_components = observation.ObservationComponent()

        sofa_components_code = codeableconcept.CodeableConcept()
        resp_coding = coding.Coding()
        resp_coding.code = component
        resp_coding.system = 'https://www.netzwerk-universitaetsmedizin.de/fhir/CodeSystem/sofa-score'

        sofa_components_code.coding = [resp_coding]
        sofa_components.code = sofa_components_code

        sofa_components_value = codeableconcept.CodeableConcept()
        resp_valueCodeableConcept_coding = coding.Coding()
        resp_valueCodeableConcept_coding.system = 'https://www.netzwerk-universitaetsmedizin.de/fhir/CodeSystem/sofa-score'
        resp_valueCodeableConcept_coding.code = f'{component}{sofa_underscores[component]}'

        sofa_components_value.coding = [resp_valueCodeableConcept_coding]
        sofa_components.valueCodeableConcept = sofa_components_value

        list_of_sofa_components.append(sofa_components)

    sofa_observation.component = list_of_sofa_components

    return sofa_observation


def createSofaProcedure(ids):

    sofa_procedure = procedure.Procedure()

    sofa_procedure.id = str(ids['prod_id'])

    status = 'completed'
    sofa_procedure.status = status

    prod_id = str(ids['prod_id'])

    identifier = procedure.identifier.Identifier()
    identifier.system = f'https://fhir/hospital/{ids["org_id"]}'
    identifier.value = prod_id
    sofa_procedure.identifier = [identifier]

    performer = procedure.ProcedurePerformer()
    performer.id = '1234'
    performer.actor = 'Automated SOFA Computation' # own pipeline as device referred

    fhir_date = fhirdate.FHIRDate(str(date.today()))
    sofa_procedure.performedDateTime = fhir_date

    code = codeableconcept.CodeableConcept()
    procedure_coding = coding.Coding()
    procedure_coding.system = 'http://snomed.info/sct'
    procedure_coding.code = '1036761000000109'
    procedure_coding.display = 'Assessment using Sequential Organ Failure Assessment score'
    code.coding = [procedure_coding]
    sofa_procedure.code = code

    subject = fhirreference.FHIRReference()
    pat_id = ids['pat_id']
    subject.reference = f'Patient/{pat_id}'
    sofa_procedure.subject = subject

    return sofa_procedure


def createSofaDevice(ids):

    sofa_device = device.Device()

    sofa_device.id = str(ids['dev_id'])

    identifier = device.identifier.Identifier()
    identifier.system = f'https://fhir/hospital/{ids["org_id"]}'
    identifier.value = str(ids['dev_id'])
    sofa_device.identifier = [identifier]

    status = 'active'
    sofa_device.status = status

    name = device.DeviceDeviceName()
    name.name = 'Automated SOFA Computation Software'
    name.type = 'other'
    sofa_device.deviceName = [name]

    type = codeableconcept.CodeableConcept()
    type_coding = coding.Coding()
    type_coding.system = 'http://snomed.info/sct'
    type_coding.code = '466917005'
    type_coding.display = 'Risk-management information system application software (physical object)'
    type.coding = [type_coding]
    sofa_device.type = type

    owner = fhirreference.FHIRReference()
    owner.reference = f'Organization/{ids["org_id"]}'
    sofa_device.owner = owner

    # version, etc. could also be added

    return sofa_device


def createNewPatient(ids, source_server, target_server, headers):
    '''
    If a target server does not allow to post a patient with an assigned id, this will create a new patient on the
    target server and return the new patient ID from it
    '''

    source_patient = requests.get(url=f'{source_server}/Patient?id={ids["pat_id"]}', headers=headers)
    source_patient = source_patient.json()

    new_patient = patient.Patient()

    birth_date = fhirdate.FHIRDate(source_patient['entry'][0]['resource']['birthDate'])
    new_patient.birthDate = birth_date

    managing_organisation = fhirreference.FHIRReference()
    managing_organisation.reference = f'Organization/{ids["org_id"]}'
    new_patient.managingOrganization = managing_organisation

    identifier = patient.identifier.Identifier(source_patient['entry'][0]['resource']['identifier'][0])
    identifier.system = f'https://fhir/hospital/{ids["org_id"]}'
    identifier.value = ids["pat_id"]
    assigner = fhirreference.FHIRReference()
    assigner.reference = f'Organization/{ids["org_id"]}'
    identifier.assigner = assigner

    new_patient.identifier = [identifier]

    req = requests.post(f'{target_server}', headers=headers, data=json.dumps(new_patient.as_json()))

    new_patient_id = req.json()['id']

    new_patient.id = new_patient_id

    fname = 'Patient-SOFA-' + str(new_patient_id) + '.json'
    with open('data/' + fname, 'w') as outfile:
        json.dump(new_patient.as_json(), outfile, indent=4)

    return new_patient_id


def setNewReferences(patient_id, sofa_observation, sofa_procedure):
    '''
    If a new patient was created for the target server, the subject references on the observation and procedure need to
    be reassigned
    '''

    subject = fhirreference.FHIRReference()
    subject.reference = f'Patient/{patient_id}'
    sofa_observation.subject = subject
    sofa_procedure.subject = subject

    return sofa_observation, sofa_procedure
