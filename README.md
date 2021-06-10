# UOCIS322 - Project 7 #

Author: Vladimir Shatalov
Address: vvs@uoregon.edu



This update adds authentication and login to brevet time calculator service.

The front end is now navigated through base.html, with the index page (brevets calculator), login and register tabs. 

There are two new functions: register user and log in. When you try to register a new user, the username and the password are sent from the html page to website.py where the password gets hashed. From there the username and the hashed password are sent to the api.py register class. The register class hashes the password again and checks the users database for a user with that name, and if one already exists a 400 error is returned along with a message. If not the new user and their hashed password (double hashed now) are added to the database.

When you log in, the password once again gets hashed in the website.py and sent along with the username to the token class in api.py. There we first search for a username with a matching name in the database, if a user is not found a 401 error is returned along with a message. If the uses is found we use the verify_password function to check the password against the one stored in the database. If the passwords match we return a message, token, valid time and the user id back to website.py. If the passwords do not match a 401 error is returned along with a message. 

Once back in the website.py login function an instance of a user is created using the user ID, name and the token. Then the flask session is updated with the username and token.

At this point the user is logged in and will have access to the brevets times. The listAll, listOpenOnly and listCloseOnly functions are now login required. Every time one of them is called, the user token is passed along with the data request and checked in the corresponding function within the api.py. If the token is valid and not expired, the data is returned, otherwise a 401 error and the token status are returned.

Now I did add the functionality of logging the user out when the token is invalid or expired, you will be logged out of the session and redirected back to the login page. Unfortunately the redirect is happening with a page-within-a-page situation, and after trying many different ways I could not figure out how to resolve that.      
