# [@GratisBot](https://twitter.com/GratisBot)
## An interactive Twitter bot that gives users free and 100% off udemy courses!
![Profile](https://i.imgur.com/OOTBvSw.png)
### Languages supported:
- Spanish
- English
- German
- French
- Portuguese
### To get courses, tag or reply to the bot with the format specified for your preferred language
(Including @GratisBot)

- Spanish: Dame (cantidad del 1-3) cursos de (tema)
- English: Give me (amount 1-3) courses about (topic)
- German: Gibt mir (Menge 1-3) Kurse uber (Thema)
- French: Donnez moi (montant 1-3) cours (sujet)
- Portuguese: Dê-me (quantidade de 1-3) cursos de (tópico)

Important notice:
If you want the bot to always give you new courses, it is important that you follow it.
Due to storage limitation, @GratisBot only remembers data from followers!

### Daily courses and discounts
Every 12 hours, @GratisBot gets the most requested topics and posts new courses about them

Every 3 hours, @GratisBot searches for Udemy 100% coupons in the web. The bot always tries to post the freshest discounts.
However, it doesnt guarantee that at the time when you click, it will still be available. To always be one of the firsts,
turn the bot's notifications on.

### How it works behind scene
To interact with twitter, the bot uses tweepy libraries.
To access udemy courses, the bot uses udemy library. 

Everytime a course is needed, the bot will search in its database for courses with the specified characteristics.
If there are no results in the database or the amount of courses is not satisfied, the bot connects to udemy API and
obtains a list of course json files. It then uses the courses for the task required and saves them into the database system.
This serves to optimize the program and avoid unnecessary requests to APIs or websites to be scraped.

For its lang and settings system, the bot reads files and converts them into dictionaries

To make the bot 24/7, and run different tasks asynchronously, Flask was implemented.

Every X time, monitors in Uptimerobot.com send https request with different routes.
Each route serves to run a specific task (e.g. checking user replies or posting discounts).

![](https://i.imgur.com/Al4mmlj.png)
