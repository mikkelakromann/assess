ASSESS - Analytical Scenario and Storyline Evaluation Support System

ASSESS is a Django app supporting scientific quantitative modelling by providing :
- database storage for modelling inputs and ouputs
- web-based user interface for managing input data, executing the scientific model and viewing output data 
- other interfaces for importing and exporting data to other applications
- organising various runs of the scientific modelling into so-called scenarios and storylines


INSTALLATION

PHASE I: Create project and apps
################################
I.1. Start Django project named assess: 
$ django-admin startproject assess 

I.2. Create items app
$ cd assess
$ python manage.py startapp items
Edit assess/settings.py - add to the list INSTALLED_APPS the entry/line: 'items.apps.ItemsConfig',


I.3 Create tables app


I.4 Create results app


PHASE II: Initialse and customise
II.1 Modify the file: assess/settings.py 
- in the TEMPLATES list: 'DIRS': [ BASE_DIR + '/templates/', ],
- in STATIC_URL = '/static/'


II.2 Set up database by editing assess/settings.py
Suit the DATABASES section to your need

II.3 Set up database
$ python manage.py makemigrations
$ python manage.py migrate

II.4 Start the webserver
$ python manage.py runserver

