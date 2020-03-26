# Frog.a.Day

This is the codebase that sits behind https://frogaday.com.  While the entirety of the codebase is functional, I would not recommend this directory structure for Flask applications.  The [Flask-Starter](https://github.com/berubejd/Flask-Starter) layout is more ideal from my perspective although there may be better ways still.

## Screenshots

![Landing](images/landing.png?raw-true)

![Calendar](images/calendar.png?raw-true)

## Libraries

This project uses a small number of libraries.

[Flask-User](https://github.com/lingthio/Flask-User) was a quick method to get account management working for this application but required the use of the [fork provided by wayne-li2](https://github.com/wayne-li2/Flask-User) which was built into the pip package [Flask-User-AWS](https://pypi.org/project/Flask-User-AWS/) in order to work on AWS Elastic Beanstalk.  Login and registration pages utilize the provided method for customization rather than use the internally provided pages, as well.

## Configuration

Most of the configuration of this app can be accomplished via environment variables.  These can be found in the [options.config](.ebextensions/options.config) file.

## Elastic Beanstalk Extensions

The [.ebextensions](.ebextensions/) directory contains a number of helpful Apache and Elastic Beanstalk configuration snippets that will be applied if this application is run on AWS Elastic Beanstalk.