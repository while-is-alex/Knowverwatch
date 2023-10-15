![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Django](https://img.shields.io/badge/django-%23092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-%234169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/celery-%2337814A?style=for-the-badge&logo=celery&logoColor=white)
![Amazon Elastic Beanstalk](https://img.shields.io/badge/elasticbeanstalk-%23232F3E?style=for-the-badge&logo=amazonaws&logoColor=white)
![Amazon S3](https://img.shields.io/badge/amazons3-%23569A31?style=for-the-badge&logo=amazons3&logoColor=white)
![Amazon RDS](https://img.shields.io/badge/amazonrds-%23527FFF?style=for-the-badge&logo=amazonrds&logoColor=white)

# Knowverwatch
Knowverwatch is a website for Overwatch League viewers to interact with the league's API data in a visual, interactive experience.

## Deployment
This project is deployed on AWS and can be accessed at http://knowverwatch.us-east-1.elasticbeanstalk.com.

## Technologies
+ Overwatch League's API
+ AWS Elastic Beanstalk
+ AWS S3
+ AWS RDS
+ Django
+ PostgreSQL
+ OOP
+ Celery
+ Redis

## Environment variables
To run this project locally, you will need to run it using `python3 manage.py runserver --nostatic` or refactor the code in settings.py to serve static files locally. You will also need to provide the following environmental variables:

+ `CLIENT_ID` - Client ID from your [Blizzard account](https://develop.battle.net/documentation/guides/getting-started).
+ `CLIENT_SECRET` - Client secret from your Blizzard account.

To run this project on AWS, you will need to provide the following environmental variables:

+ `POSTGRES_USER` - Postgres user registered in AWS's RDS.
+ `POSTGRES_PASSWORD` - Postgres password registered from AWS's RDS.
+ `AWS_ACCESS_KEY_ID` - Access key generated in AWS's S3.
+ `AWS_SECRET_ACCESS_KEY` - Secret access key generated in AWS's S3.

## Features

+ Spoilers: Turns spoilers on or off, depending on the user's choice, remembering the user's choice throughout the website and in future sessions as well.
+ Home page: Dynamically fetches and displays the current stage or tournament standings on the home page, dividing the data in between west and east regions.
+ Teams page: Displays all the teams in the league, offering the possibility to filter by region. Styles adapt to each team's colors.
+ Team details page: Displays a team's titles, roster and past matches. The background image adapts to display each team's logo.
+ Matches details page: Displays the last updated score, provides a link to the match on youtube, displays each individual map score and displays the players who played in that match and the heroes played.
+ Players page: Displays all the players in the league, showing which players are currently in a team or not.
+ Player details page: Displays a player's information, awards and heroes statistics.
+ Compare players page: Select players and heroes to compare player's statistics.

### Technical features
+ Requests to Overwatch League's API simplified through Object Oriented Programming.
+ Asynchronous creation and update of the database using Redis as the message broker and Celery as the worker.
+ Backend written in Python to dynamically fetch from the database the requested data.
+ Using Django Template Language, generates each individual page from a single HTML document.
+ Mobile compatible.

## Roadmap

+ Add data from past seasons (2019 to 2021).
+ Add a game to decide who's the best player of all time.
+ Add a page to see statistics per hero.
+ Implement asynchronous updates in AWS.
+ Implement web sockets to update data displayed in an open page in near real time, such as scores from an ongoing match.

## Preview
The website supports a light mode as well, but all preview images are in dark mode.

![home-page.png](https://i.ibb.co/MZJJQwk/standings.png)
![teams.png](https://i.ibb.co/ssXfCHt/teams.png)
![team-details-page.png](https://i.ibb.co/5672NSp/team-page.png)
![past-matches.png](https://i.ibb.co/5xfRFgF/past-matches.png)
![match-details.png](https://i.ibb.co/LZLK1pw/match-details.png)
![played-in-match.png](https://i.ibb.co/L5G8WK0/played-in-match.png)
![players.png](https://i.ibb.co/brwJy5y/players.png)
![player-details-page.png](https://i.ibb.co/nzPgwG8/player-page.png)
![player-hero-stats.png](https://i.ibb.co/G5gjgGT/hero-stats.png)
![compare-players.png](https://i.ibb.co/d6BvQS4/compare-players.png)
