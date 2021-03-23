# web-submit
Simple [fastapi](https://fastapi.tiangolo.com/) based web server for submitting APK files and getting them analysed. 
This app uses a small PostgreSQL DB to cache already analysed results.

# How to run this program?

## DB initialisation & preparation steps

**Note**: these instructions assume python 3.7 or higher.

  1. Create a virtual env: ``virtualenv venv``
  2. Install the requirements: ``pip install -r requirements.txt``
  3. Install PostgreSQL if needed according to your OS recommendations
  4. Create the (postgres) binhash database: 
```bash
sudo -u postgres
createdb bincache
createuser bincache
psql bincache
  GRANT all on database bincache to bincache;
  GRANT all on cache to bincache;
Ctrl-D
exit

cd db; psql -U binache bincache < db.sql
```

  5. Make sure the new DB is accessible:
```
  psql -U bincache bincache
  \d cache
```
You  should see the database structure.

## Running the server / the app via uvicorn

**Note**: the following section describes how to run a development server. This should not 
be run on a system which is directly available to the internet, due to the potential security 
implications. Please follow the fastapi docs on how to properly have a HTTPs proxy in front of 
uvicorn or similar ASWGI application servers.


  1. create a virtualenv: ``virtualenv --python=python3 venv``
  2. source the virtual env: ``source venv/bin/activate``
  3. adapt the ENV file which sets system environment variables to your need, then source it: ``source ENV``. You can take the ENV.sample file and edit it and rename it to ``ENV``.
  4. Double check if the config and especially the DB username is correct in the file ``config.py``. Adapt as needed. The example above used a username "bincache" for the "bincache" database which is residing on "localhost".
  5. Start uvicorn:

```bash
uvicorn --reload --debug app.main:app
```

Now direct your browser to http://localhost:80/api/v1/docs. You should see the OpenAPI-generated interactive RESTful API.
Please try to upload a binary to the application.

The code which returns ``contains_trackers`` and ``contains_adware`` is still a sample function and should be replaced by a proper call.
This code was not part of the MAL2 project, but is there for future projects.

Try uploading a .apk file via http://localhost:80/api/v1/docs.
You should see the uploaded binary in the folder which was specified as UPLOAD_PATH in config.py


# Docker

Build the docker container via :

```bash
docker build  -t mal2:latest .
```

Run it via:
```bash
docker run --rm --name mal2test  -e LOG_LEVEL="info" --network=host --gpus=all --ipc=host mal2:latest
```

## About MAL2

The MAL2 project applies Deep Neural Networks and Unsupervised Machine Learning to advance cybercrime prevention by a) automating the discovery of fraudulent eCommerce and b) detecting Potentially Harmful Apps (PHAs) in Android.
The goal of the MAL2 project is to provide (i) an Open Source framework and expert tools with integrated functionality along the required pipeline – from malicious data archiving, feature selection and extraction, training of Machine Learning classification and detection models towards explainability in the analysis of results (ii) to execute its components at scale and (iii) to publish an annotated Ground-Truth dataset in both application domains. To raise awareness for cybercrime prevention in the general public, two demonstrators, a Fake-Shop Detection Browser Plugin as well as a Android Malware Detection Android app are released that allow live-inspection and AI based predictions on the trustworthiness of eCommerce sites and Android apps.

The work is based on results carried out in the research project [MAL2 project](https://projekte.ffg.at/projekt/3044975), which was partially funded by the Austrian Federal Ministry for Climate Action, Environment, Energy, Mobility, Innovation and Technology (BMK) through the ICT of the future research program (6th call) managed by the Austrian federal funding agency (FFG).
* Austrian Institute of Technology GmbH, Center for Digital Safety and Security [AIT](https://www.ait.ac.at/)
* Austrian Institute for Applied Telecommunications [ÖIAT](https://www.oiat.at)
* X-NET Services GmbH [XNET](https://x-net.at/de/)
* Kuratorium sicheres Österreich [KSÖ](https://kuratorium-sicheres-oesterreich.at/)
* IKARUS Security Software [IKARUS](https://www.ikarussecurity.com/)

More information is available at [www.malzwei.at](http://www.malzwei.at)

## Contact
For details on behalf of the MAL2 consortium contact: 
Andrew Lindley (project lead)
Research Engineer, Data Science & Artificial Intelligence
Center for Digital Safety and Security, AIT Austrian Institute of Technology GmbH
Giefinggasse 4 | 1210 Vienna | Austria
T +43 50550-4272 | M +43 664 8157848 | F +43 50550-4150
andrew.lindley@ait.ac.at | www.ait.ac.at
or
Woflgang Eibner, X-NET Services GmbH, we@x-net.at

## License
The MAL2 Software stack is dual-licensed under commercial and open source licenses. 
The Software in this repository is subject of the terms and conditions defined in file 'LICENSE.md'
