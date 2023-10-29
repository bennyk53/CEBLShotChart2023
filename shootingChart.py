import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import pymongo

def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    hoop = Circle((160, 41.5 ), radius=4.57, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((141.7, 34), 36.6, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((111, 10), 98, 116, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    #inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)

    # Create free throw top arc
    top_free_throw = Arc((160, 126), 98, 98, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    #bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color, linestyle='dashed')

    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((160, 50), 24, 24, theta1=0, theta2=180, linewidth=lw, color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((28, 10), 0, 60.8, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((291.8, 10), 0, 60.8, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the
    # threes
    three_arc = Arc((160, 70), 264, 236.5, theta1=0, theta2=180, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((160, 290), 36, 36, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box,top_free_throw,
                     corner_three_a,
                      corner_three_b, three_arc, center_outer_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((10,10), 300, 280, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax

################################################
st.title('CEBL 2023 Shooting Charts')

client = pymongo.MongoClient("mongodb+srv://cebl:cebl@cebl0.ro1fza0.mongodb.net/?retryWrites=true&w=majority",tls=True,tlsAllowInvalidCertificates=True)

mydb = client["CEBL"]
mycol = mydb["Teams"]
col1, col2 = st.columns(2)

teams = ['Select team....','Ottawa BlackJacks','Winnipeg Sea Bears','Edmonton Stingers','Brampton Honey Badgers','Vancouver Bandits','Calgary Surge','Saskatchewan Rattlers'
         ,'Niagara River Lions','Scarborough Shooting Stars','Montreal Alliance']
with col1:
    teamName = st.selectbox('Select Team',teams,)

try:
    
    getTeam = {'name':teamName}
    t = mycol.find_one(getTeam)
    
    timg = t['img']
    teamID = t['_id']

    with col1:
        st.image(timg, width = 250)

    mycol = mydb["PlayerGameStats"]

    getPlayers = {'teamID':teamID}
    players = mycol.find(getPlayers).distinct('playerID')

    mycol = mydb["Players"]

    playerList = ['Select player....']

    for p in players:
      getPlayer = {'_id':p}
      player = mycol.find_one(getPlayer)
      playerList.append(player['firstName'] +' '+player['lastName'])

    with col2:
        playerName = st.selectbox('Select Player',playerList,)

    mycol = mydb["Players"]

    x_data = []
    y_data = []
    
    searchName = playerName.split(' ')
    
    fname = searchName[0]
    lname = searchName[1]

    getPlayer = {'firstName':fname,'lastName':lname}
    p = mycol.find_one(getPlayer)

    img = p['img']
    getId = p['_id']


    with col2:
        st.image(img,width=250)

    mycol = mydb["PlayerGameShotChart"]

    getShots = {'playerID':getId}
    shots = mycol.find(getShots)

    for s in shots:
      x = s['x']
      y = s['y']
      x_data.append(x)
      y_data.append(y)


    plt.hexbin(x_data, y_data, gridsize = 15, extent=[0,320,0,300], cmap ='Blues',mincnt=0)
    draw_court(outer_lines=True)
    plt.axis('off')
    st.pyplot(plt.gcf())

except:
    print()
