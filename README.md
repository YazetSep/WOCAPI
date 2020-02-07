# WhatsOnCampusRestAPI

This is the What's on Campus API. This API has everything that serves and connects with the apps and the websites.
It is important to understand what each branch does. Since some where not finished. I hope you may continue with this work and help the community. 
 
## Braches
Only these branches are relevant. The other's are merged branches that are not important. 
#### master
This is the mainly working version but is not clean since it was the first API that was made. It also mixes some old divisions that were between mobile and website versions.
#### Refactor
This branch is the start of the new API style which compartmentalizes the modules in a more organized way and doesn't need decorations. This is missing some functionality tho. 
#### testing
This is a CI (continuous integration) branch. This branch would automatically deploy into the beta version of the server. To get this working you need a server and setup the appropriate webhooks. 
This also needs approval and can be merge only to not accidentally commit to this branch. SHOULD NEVER BE USED TO EDIT DIRECTLY
#### deployment
This is a CI (continuous integration) branch. This branch would automatically deploy to the live version of the website. Should not be edited. This was the last working version

## Running 
You need to have a database first or it will cause problems. Install postgreSQL in a server with docker or locally then run 
    
Install packages 

    pip3 install -r requirements.txt

To run 

    python3 main.py

P.S. I would recommend you use Docker container and a python enviorment for consistency in development. 

## Other details 
* ***wsgi*** - This would be use to run on the server. Look up and read about WSGI to understand this. 
* ***emailer*** - This was a test to email. 
* ***databses*** - SQLAlchemy automatically makes tables when you run but be careful there are options that can replace the whole database when testing. This command is not currently in the branch but keep it in mind when dealing with this. 

## Future work 
Even if everything seems like it's working all features should be checked. We tried to not let things slip through the cracks, but there's also things that we didn't get to fix.
If you've never worked on a website and API's you will learn a lot from all this. Good luck!  




