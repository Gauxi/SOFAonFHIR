# SOFAonFHIR Prototype Pipeline

This flask prject was build for a master thesis project to automatically calculate the SOFA score from (simulated) 
FHIR Resources and return it as FHIR Resources.

## Installation
- It is recommended to install the fhir client directly from the git repository:
`pip install git+https://github.com/smart-on-fhir/client-py.git `
- Install Requirements:
`pip install -r requirements.txt`
- Adjust your config.py
- You can use an open FHIR Test Server or create your own Firely Server: 
`http://docs.simplifier.net/firelyserver/deployment/deployment.html`

## Start with
`python3 .\run.py`

This application can be used via the provided web interface, with REST Api calls e.g. via Postman or with a curl 
command.

## REST API Call
`<base_url_server>/SOFA_API/?source_p_id=<source_patient_id>&target_p_id=<target_patient_id>&source=<source_server>&target=<target_server>&auth_key=<key>&org=<organisation>&new_patient=<True>`

## Curl command
`curl -H "Content-Type: application/json" -d '{"source_p_id":"source_patient_id","target_p_id":"target_patient_id", "source":"source_server", "target":"target_server","auth_key":"key", "org":"organisation", "new_patient": "True"}' -v <base_url_server>/SOFA_API_CURL/`

## DOCKER with provided docker file
- Build Image: sudo docker build -t <your_username>/repo .
- Run Container: sudo docker run -p 5000:5000 <your_username>/repo 
- Publish Image: sudo docker push <your_username>/repo
- Pull Image: sudo docker pull <your_username>/repo

* A public image is provided on gauxi/sofa_on_fhir_pipeline:latest

## Copyright and License
* [MIT](https://tldrlegal.com/license/mit-license)

## Links
* [FHIR profiles from the Medical Informatics Initiative (MII)](https://simplifier.net/organization/koordinationsstellemii)
* [SMART on FHIR Python Client](http://docs.smarthealthit.org/client-py/index.html)
