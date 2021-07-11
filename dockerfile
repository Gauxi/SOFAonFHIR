FROM python:3

WORKDIR /SOFAonFHIR

COPY requirements.txt requirements.txt
RUN pip3 --no-cache-dir install -r requirements.txt git+https://github.com/smart-on-fhir/client-py.git

COPY . .

EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]