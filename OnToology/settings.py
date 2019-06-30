"""
Django settings for OnToology project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEDIA_ROOT = BASE_DIR+'/media/'
MEDIA_URL = '/media/'

LOGIN_URL = '/login'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = '!pt9$ocsv9m1@_$eiq(9=0&_=wg@-^&f$f0j#k57l&g71$av(n'
SECRET_KEY = 'xj1c6fel(z5@=%(br!j)u155a71j*^u_b+2'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_mongoengine',
    'django_mongoengine.mongo_auth',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',  # From django 1.7
]

ROOT_URLCONF = 'OnToology.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR+'/templates',],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'OnToology.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'




#### Mongo Engine configs #########


test_conf = {'local': False,  # doing test
             'fork': False,  # perform fork
             'clone': False,  # perform clone
             'push': False,  # push the changes to GitHub
             'pull': False,  # to create a pull request from the forked on
             }

try:
    from localwsgi import *
    print "importing environ from local wsgi"
except Exception as e:
    print "no local wsgi"
    print e

# MongoDB settings
MONGODB_DATABASES = {
    'default': {'name': 'OnToology'}
}

environ = os.environ
print("environ: ")
print(environ)

print("type: "+str(type(environ)))
# print("host in environ: "+environ['host_db'])

if 'db_host' in environ:
    print("yes db_host in environ")
    host_db = environ['db_host']
    if 'db_port' in environ:
        host_db+=":"+str(environ['db_port'])
    MONGODB_DATABASES['default']['host'] = host_db
    print("updated with host: "+str(MONGODB_DATABASES['default']['host']))
    if 'db_name' in environ:
        MONGODB_DATABASES['default']['name'] = environ['db_name']
        print("updated with host: " + str(MONGODB_DATABASES['default']['name']))

else:
    print("db_host is not in environ")

print("MONGODB: "+str(MONGODB_DATABASES))





GITHUB_LOCAL_APP_ID = '3995f5db01f035de44c6'
GITHUB_LOCAL_API_SECRET = '141f896e53db4a4427db177f1ef2c9975e8a3c1f'


AUTH_USER_MODEL = 'mongo_auth.MongoUser'
AUTHENTICATION_BACKENDS = (
    'django_mongoengine.mongo_auth.backends.MongoEngineBackend',
)

SESSION_ENGINE = 'django_mongoengine.sessions'
SESSION_SERIALIZER = 'mongoengine.django.sessions.BSONSerializer'  # from django 1.7 and old mongo

host = 'http://ontoology.linkeddata.es'
if 'host' in os.environ:
    host = os.environ['host']
local = False
if 'OnToology_home' in os.environ and os.environ['OnToology_home'].lower() == "true":
    local = True
    host = 'http://127.0.0.1:8000'
    client_id = GITHUB_LOCAL_APP_ID
    client_secret = GITHUB_LOCAL_API_SECRET
    print "Going local"
else:
    print "Going remote"
    print os.environ



#
# from mongoengine import connect
# MONGO_DATABASE_NAME = "OnToology"
# if "db_name" in os.environ:
#     MONGO_DATABASE_NAME = os.environ["db_name"]
#
# if 'db_username' not in os.environ or os.environ['db_username'].strip() == '':
#     print "no auth"
#     connect(MONGO_DATABASE_NAME)
# else:
#     print "with auth"
#     connect(MONGO_DATABASE_NAME, host=os.environ['db_host'], port=int(os.environ['db_port']),
#             username=os.environ['db_username'], password=os.environ['db_password'],
#             )
#             #authentication_mechanism='MONGODB-CR')
#             #authentication_mechanism='SCRAM-SHA-1')
