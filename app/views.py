from flask import render_template, request, jsonify

from app import app
from app.calculationsScores import calc_underscores, calc_total_sofa_score
from app.creatingSOFAResource import createSofaResources


@app.route("/", methods=['POST', 'GET'])
def root():

    # Gets all parameters from frontend form
    if request.method == 'POST':
        source_patient_id = request.form['source_p_id']
        target_patient_id = request.form['target_p_id']
        organisation_id = request.form['org_id']
        source_server = request.form['source_server']
        target_server = request.form['target_server']
        authorization_key = request.form['auth_key']
        create_new_patient = request.form.get('new_patient_check', False)

        # If parameters are missing, loads them from config
        if not organisation_id:
            organisation_id = app.config['DEFAULT_ORGANISATION']
        if not source_server:
            source_server = app.config['SOURCE_SERVER']
        if not target_server:
            target_server = app.config['TARGET_SERVER']

        headers = {
            "Accept": "application/fhir+json; fhirVersion=4.0",
            "Content-Type": "application/fhir+json; fhirVersion=4.0",
            "Authorization": f"access-key {authorization_key}"
        }

        # Source patient ID is mandatory for score calculation
        if source_patient_id:
            patient_str = 'subject=Patient/' + source_patient_id
            sofa_underscores = calc_underscores(patient_str, source_server)
            sofa_score = calc_total_sofa_score(sofa_underscores)

            # If target patient is not provided, creates a new one on the target server
            if not target_patient_id:
                response, new_patient = createSofaResources(source_patient_id, organisation_id, sofa_underscores,
                                                            sofa_score, source_server, target_server, headers,
                                                            create_new_patient)
            else:
                response, new_patient = createSofaResources(target_patient_id, organisation_id, sofa_underscores,
                                                            sofa_score, source_server, target_server, headers,
                                                            create_new_patient)

            if new_patient:
                return render_template("index.html", SOFA_score=sofa_score, sub_scores=sofa_underscores,
                                       status=response, patient_id=source_patient_id, new_patient_id=new_patient)
            else:
                return render_template("index.html", SOFA_score=sofa_score, sub_scores=sofa_underscores,
                                       status=response, patient_id=target_patient_id)

    return render_template("index.html")


# REST API Call eg via Postman
# <base_url_server>/SOFA_API/?source_p_id=<source_patient_id>&target_p_id=<target_patient_id>&source=<source_server>& //
# target=<target_server>&auth_key=<key>&org=<organisation>&new_patient=<True>
@app.route("/SOFA_API/", methods=['POST'])
def apiCall():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    source_patient_id = request.args.get('source_p_id')
    target_patient_id = request.args.get('target_p_id')
    organisation_id = request.args.get('org')
    source_server = request.args.get('source')
    target_server = request.args.get('target')
    new_patient = request.args.get('new_patient')
    authorization_key = request.args.get('auth_key')

    if not source_patient_id:
        return jsonify({"msg": "Missing patient ID parameter"}), 400

    if not organisation_id:
        organisation_id = app.config['DEFAULT_ORGANISATION']
    if not source_server:
        source_server = app.config['SOURCE_SERVER']
    if not target_server:
        target_server = app.config['TARGET_SERVER']
    if not new_patient or new_patient == 'False':
        new_patient = False

    headers = {
        "Accept": "application/fhir+json; fhirVersion=4.0",
        "Content-Type": "application/fhir+json; fhirVersion=4.0",
        "Authorization": f"access-key {authorization_key}"
    }

    patient_str = 'subject=Patient/' + source_patient_id
    sofa_underscores = calc_underscores(patient_str, source_server)
    sofa_score = calc_total_sofa_score(sofa_underscores)

    if not target_patient_id:
        response, new_patient = createSofaResources(source_patient_id, organisation_id, sofa_underscores,
                                                    sofa_score, source_server, target_server, headers, new_patient)
    else:
        response, new_patient = createSofaResources(target_patient_id, organisation_id, sofa_underscores,
                                                    sofa_score, source_server, target_server, headers, new_patient)

    return jsonify(response), 200


# curl -H "Content-Type: application/json" -d '{"source_p_id":"source_patient_id","target_p_id":"target_patient_id", //
# "source":"source_server", "target":"target_server","auth_key":"key", "org":"organisation", "new_patient": "True"}' //
# -v <base_url_server>/SOFA_API_CURL/
@app.route("/SOFA_API_CURL/", methods=['POST'])
def curlApiCall():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    source_patient_id = request.json.get('source_p_id')
    target_patient_id = request.json.get('target_p_id')
    organisation_id = request.json.get('org')
    source_server = request.json.get('source')
    target_server = request.json.get('target')
    new_patient = request.json.get('new_patient')
    authorization_key = request.json.get('auth_key')

    if not source_patient_id:
        return jsonify({"msg": "Missing patient ID parameter"}), 400

    if not organisation_id:
        organisation_id = app.config['DEFAULT_ORGANISATION']
    if not source_server:
        source_server = app.config['SOURCE_SERVER']
    if not target_server:
        target_server = app.config['TARGET_SERVER']
    if not new_patient or new_patient == 'False':
        new_patient = False

    headers = {
        "Accept": "application/fhir+json; fhirVersion=4.0",
        "Content-Type": "application/fhir+json; fhirVersion=4.0",
        "Authorization": f"access-key {authorization_key}"
    }

    patient_str = 'subject=Patient/' + source_patient_id
    sofa_underscores = calc_underscores(patient_str, source_server)
    sofa_score = calc_total_sofa_score(sofa_underscores)

    if not target_patient_id:
        response, new_patient = createSofaResources(source_patient_id, organisation_id, sofa_underscores,
                                                    sofa_score, source_server, target_server, headers, new_patient)
    else:
        response, new_patient = createSofaResources(target_patient_id, organisation_id, sofa_underscores,
                                                    sofa_score, source_server, target_server, headers, new_patient)

    return jsonify(response), 200