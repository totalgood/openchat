## Running the bot with Docker

* First install Docker (if on Mac OS you'll need to set the available RAM higher than 4GB for the Docker VM, this is needed beacuse of the JVM overhead with SUtime)

* There is a current dependency on Java being installed on the machine that is running the Docker VM, this will be removed in the furture. For the moment a user needs to create a `python-sutime` directory in the root of the project and follow the instructions [here](https://github.com/FraBle/python-sutime) to install the SUtime dependencies.

### Setting up local_settings.py
This file is used to hold the development settings/secrets for the bot. You will need to create this file in this location: openchat/openchat/local_settings.py

This file should contain the Django SECRET_KEY, DATABASES, and DEBUG values used by Django.

### Start up commands
All commands below should be run in the root directory of the project unless otherwise stated.

* Run the command `docker-compose build`, this will build the images needed for the docker cluster

* Run the command `docker-compose up`, this will start the project and run the django server on localhost:8000

### Shelling into the openchat container
In order to turn on the bot and to run Celery you'll need to shell into the openchat container and run the setup steps described below. Both of these steps will be added to the container start up at a later date.

* In a different terminal run `docker exec -it openchat_nginx_1 bash`, this will start up a bash terminal inside the openchat container. The following bot commands will need to be run from inside the openchat_web_1 container.

#### Turning on the bot
At the moment we will be using the load_test_bot.py script to work on developing new features. In order for this bot to work it needs access to the openchat/openspaces/secrets.py file. You'll need to create this file and add a dictionary called `sender` with the Twitter CONSUMER_SECRET, CONSUMER_KEY, ACCESS_TOKEN, and ACCESS_TOKEN_SECRET values.

Once you're inside the running docker container and the secrets.py file has been added you can turn the bot on by running: `python load_test_bot.py`


#### Turning on Celery
To turn Celery on run the command below in a seperate terminal from the two created in the steps above

* `docker exec celery -A openchat worker -B -l info`


