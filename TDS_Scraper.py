from pickle import NONE
import time 
from bs4 import BeautifulSoup 
import requests 
import mysql.connector


time.sleep(2) 

headers = {"user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/65.0.3325.162 Safari/537.36",
            "from": "Joas Cerutti joascerutt@gmail.com"}

rows = []

#open the website 
url = "https://www.topdrawersoccer.com/club-soccer/club-soccer-team-rankings/men/u18/6/1346"

#Program Name: Soccer website scraper 

#Purpose: Create a function that scrapes data from soccer website 

#Process: 1. Pass the url of the website into the function as a parameter
#         2. parse through the page(url html code)
#         3. Find in what tag all the data that you want to scrape is hidden in, in this case it is a table 
#           - Under table the <tbody> tag holds all the data we want to scrape
#           - find each type of data you want to scrape and store it into a list 
#               a. scrape each teams' rank add it to a list rank
#               b. scrape each teams' team name add it to a list team_name
#               c. scrape each teams' head coach add it to a list head_coach
#               d. scrape each teams' comments added it to a list comment
def scrape_content(url): # In here we are telling Python that we’re creating a 
    #function called scrape_content() that takes the argument url

    page = requests.get(url, headers=headers) #the variable page gets set to contain the HTML page, which we open using 
    #the requests library's get() function. This functions grabs the site from the web. 

    page_content = page.content #Now we using the content property from requests to encode the HTML of the 
    #page we just opened and ingested the previous line as bytes that are interpretable by BeautifulSoup.
    
    #parse the page with Beautiful Soup Library
    soup = BeautifulSoup(page_content, "html.parser") #This helps our script differentiate between HTML
    #and the sites content.
    
    
    content = soup.find("table") # we use the find() function to find a 
    #<table> class in the html code, this table class holds all the team names, location, 
    # and current standing the desing of the table, its column headers.
    

    all_groupings = content.find("tbody") #<tbody> class in the html code, this table class holds all 
    #the team names, location, and current standing
    
    team_data = all_groupings.find_all('tr')
    
    rank = []
    team_name = []
    team_id = [] # clean version of team ids 
    temp_id_list = [] # used to store messy team ids 
    temp_links_name = []
    team_links = []
    
    #clean the data
    for data in team_data: #to go through all different groupings in the website
        rank.append(data.find('td', class_='tac').get_text().strip()) # finds each team rank and adds them to list 
        temp_id_list.append(str(data.find('a', id_=''))) # finds each teamid and adds to list 
        temp_links_name.append(data.find_all('a', href_=''))
    for item in temp_links_name: # iterate throught all items in list with team id, team link, team name data
        item.pop(0) # pop out the team id data which isnt needed 
        for link in item: # iterate through each link in item of the list 
            team_name.append(link.get_text().strip()) # gets each team name, cleans up empty space, and adds to list
            team_links.append(link['href']) #get link and store in list
    
    for i in temp_id_list:
        team_id.append(i[20:25])
    
    
    zipped_lists = zip(team_id, team_name, team_links, rank)
    wrapped_zip_list = list(zipped_lists)
    #print(list(zipped_lists))
    #This creates the connection to the database server  
    #and saves it under variable name
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database = "kishimitaDB"
    )

    mycursor = mydb.cursor(buffered = True)#make a variable that points the cursor to the database
    mycursor.execute("SHOW TABLES") # this would show all the tables in the Database 

    
    sql = """INSERT INTO TEAM_INFO (`Team_Id`, `Team_Name`, `Team_Link`, `Rank`) VALUES (%s, %s, %s, %s);""" # this saves a query line that  will Insert to
    # table_name then specify which columns in the parenthesis() and then the values part acts as a place holder for 
    # the actual data that is being entered
    val = wrapped_zip_list # this is the actual values being inserted
    
    
    mycursor.executemany(sql, val)#this uses mycursor variable that is our connection to be able to write queries
    # to execute our statements saved in sql and value variables. We use this instead of exceute() because it is multiple values 


    mydb.commit() # points to our databse and it commits all 'actions' to the database
    mycursor.close() #closes the connection of the cursor 
    mydb.close() #closes the connection to the mysql database 
    
scrape_content(url)