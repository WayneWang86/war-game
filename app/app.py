from flask import Flask, Markup
import random
import assets
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# initialize firebase client
cred = credentials.Certificate("./war-game-adb13-firebase-adminsdk-98m0u-2767c36922.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://war-game-adb13-default-rtdb.firebaseio.com/"
})

app = Flask(__name__)

@app.route('/start-game')
@app.route('/start-game/<player_1>')
@app.route("/start-game/<player_1>/<player_2>")
def start_game(player_1 = None, player_2 = None):
    """
    This function handles the API call to start a game, taking two parameters
    player_1 and player_2 as the name of players. Assign default name to
    them if not given.

    Parameters:
    player_1 (str): player name
    player_2 (str): player name

    Returns:
    str: A string that used for HTML rendering to return the API call
    """

    # If the name of two players are not given
    # use default player names
    if player_1 == None:
        player_1 = "Tom"
    if player_2 == None:
        player_2 = "Jerry"

    # A list from 1 to 52 to represent each card
    deck = list(range(1, 53))
    random.shuffle(deck)

    # Evenly divide shuffled deck into two decks
    deck_1 = deck[:26]
    deck_2 = deck[26:52]
    round_cnt = 0

    game_log = "<h1 style='color: green;'>============ GAME START ============</h1><br>"
    game_log = game_log + "<p>===================================</p>"
    war = False

    # Initlize table, which contains the card played on the table
    table = []
    while len(deck_1) != 0 and len(deck_2) != 0:
        if not war:
            round_cnt += 1
            round_log = "<p style = 'font-size: 20px;'>" + "Round " + str(round_cnt) + "</p>"
            game_log = game_log + round_log

        # Each player show a card
        card_1 = deck_1.pop(0)
        card_2 = deck_2.pop(0)

        # put the card on the table
        table.append(card_1)
        table.append(card_2)

        # Get the card with suit and its value
        suit_card_1, val_1 = card_suit_val(card_1)
        suit_card_2, val_2 = card_suit_val(card_2)
        
        # add into game log
        log = "<div class='game_round' style = 'display:flex;'> \
                    <div class='player_1' style = 'margin-left:10px; margin-right:10px;'> \
                        <p style = 'font-size: 20px; font-weight: bold; margin:0;'>{}({})</p> \
                        {} \
                    </div>\
                    <div class='player_2' style = 'margin-left:10px; margin-right:10px;'> \
                        <p style = 'font-size: 20px; font-weight: bold; margin:0;'>{}({})</p> \
                        {} \
                    </div>\
                </div>".format(player_1, str(len(deck_1)), suit_card_1, player_2, str(len(deck_2)), suit_card_2)


        game_log = game_log + log
        table_log = "<p style = 'font-size: 20px; font-style: italic;'>" + "Cards on table: " + str(len(table)) + "</p>"
        game_log = game_log + table_log

        # when two players have a tie, then go into war
        if val_1 == val_2:
            # check if either player has an empty deck
            game_log = game_log + "<p class='war' style = 'color: darkred; font-size: 30px; padding: 0; margin: 0;'><span style='text-align: center; display: inline-block; font-family: 'Apple Symbols'; font-size: 100px;'>⚔⚔⚔⚔⚔WAR⚔⚔⚔⚔⚔</span></p>"

            game_over, winner = check_status(deck_1, deck_2, player_1, player_2)
            if game_over == 1:
                game_res = "<h1 style='font-size: 50px; color: red;'>WINNER is {}</h1>".format(winner)
                game_log = game_res + game_log + "<p class='war' style = 'color: darkred; font-size: 30px; padding: 0; margin: 0;'>No soldiers left for the war</p>" + \
                "<h1 style='font-size: 30px; color: red;'>{} is the ultimate winner!</h1>".format(winner)
                return Markup(game_log)
            
            if game_over == 2:
                game_res = "<h1 style='font-size: 50px; color: red;'>GAME TIED, NO WINNERS</h1>"
                game_log = game_res + game_log + "<p class='war' style = 'color: darkred; font-size: 30px; padding: 0; margin: 0;'>No soldiers left for the war</p>" + \
                "<h1 style='font-size: 30px; color: red;'>GAME TIED, both player have no soldiers left for the war</h1>"
                return Markup(game_log)                
            
            # Each player put a card face down to the table
            table.append(deck_1.pop(0))
            table.append(deck_2.pop(0))
            war = True
        elif (val_1 > val_2):
            random.shuffle(table)
            deck_1.extend(table)
            table = []
            war = False
        else:
            random.shuffle(table)
            deck_2.extend(table)
            table = []
            war = False
        if war:
            game_log = game_log + "<br>"
        else:
            game_log = game_log + "<p>===================================</p>"
        
        # set a hard thresold to end the game    
        if round_cnt == 500:
            if (len(deck_1) == len(deck_2)):
                game_res = "<h1 style='font-size: 50px; color: red;'>GAME TIED, NO WINNERS</h1>"
                game_log = game_res + game_log + \
                    "<h1 style='color: green;'>============ GAME ENDED ============</h1><br>" + \
                        "<h1 style='font-size: 30px; color: red;'>GAME TIED AFTER 500 ROUNDS</h1>"
            else:
                if (len(deck_1) > len(deck_2)):
                    winner = player_1
                elif (len(deck_2) > len(deck_1)):
                    winner = player_2
                
                game_res = "<h1 style='font-size: 50px; color: red;'>WINNER is {}</h1>".format(winner)
                game_log = game_res + game_log + \
                    "<h1 style='color: green;'>============ GAME ENDED ============</h1><br>" + \
                    "<h1 style='font-size: 30px; color: red;'>{} is the winner after 500 rounds!</h1>".format(winner)
                write_res(player_1, player_2, winner)
            
            return Markup(game_log)

    game_over, winner = check_status(deck_1, deck_2, player_1, player_2)

    game_res = "<h1 style='font-size: 50px; color: red;'>WINNER is {}</h1>".format(winner)
    game_log = game_res + game_log + \
        "<h1 style='color: green;'>============ GAME ENDED ============</h1><br>" + \
            "<h1 style='font-size: 30px; color: red;'>{} is the ultimate winner!</h1>".format(winner)
    
    write_res(player_1, player_2, winner)

    return Markup(game_log)

def write_res(player_1, player_2, winner):
    """
    This function takes player_1, player_2 and winner and write the game
    result into firebase

    Parameters:
    player_1 (str): player name
    player_2 (str): player name
    winner (str): the name of winner
    """
    if (winner == player_1):
        opponent = player_2
    else:
        opponent = player_1

    game_result = {
        'opponent': opponent
    }  

    ref = db.reference('game_results')
    ref.child(winner).push(game_result)

def card_suit_val(card):
    """
    This function takes one number (1-52) as input and return the card
    and value corresponding to the input.

    Parameters:
    card (int): the card number, ranging from 1 to 52

    Returns:
    str: unicode representation of the card
    int: the value of the card

    if x / 13 == 0: the card's suit is heart
    if x / 13 == 1: the card's suit is diamond
    if x / 13 == 2: the card's suit is club
    if x / 13 == 3: the card's suit is spade
    """

    val = card % 13
    if val == 0:
        val = 13
    # Ace is larger than the King
    if val == 1:
        val = 14

    if (card - 1) // 13 == 0:
        suit = assets.hearts
    elif (card - 1) // 13 == 1:
        suit = assets.diamonds
    elif (card - 1) // 13 == 2:
        suit = assets.clubs
    elif (card - 1) // 13 == 3:
        suit = assets.spades

    return suit[val - 1], val

def check_status(deck_1, deck_2, player_1, player_2):
    """
    This function checks whether there is a player has empty deck on hand

    Parameters:
    deck_1 (list): player_1's deck
    deck_2 (list): player_2's deck
    player_1 (str): player name
    player_2 (str): player name

    Returns:
    boolean: Whether the game is over (one player has empty deck)
    str: The name of the winner (empty str if the game continues)
    """
    # If both players have no cards on hand
    if (len(deck_1) == 0 and len(deck_2) == 0):
        return 2, ""
    
    # If player_1 deck is empty, then play_2 wins the game
    if (len(deck_1) == 0):
        return 1, player_2
    # If player_1 deck is empty, then play_2 wins the game
    if (len(deck_2) == 0):
        return 1, player_1
    # If either player's deck is empty, then game continues
    return 0, ""

@app.route("/leaderboard")
def read_winning_record():
    """
    This function retrive data from database and output each player's
    lifetime wins

    """
    
    # Get a reference to the winners node
    ref = db.reference().child("game_results")

    # Initialize a dictionary to store the number of wins for each player
    wins = {}

    # Loop through all the winners
    for winner in ref.get().keys():
        # Get a reference to the winner node
        player_ref = ref.child(winner)

        # Get the number of children (i.e., number of games won) for the winner node
        num_wins = len(player_ref.get().keys())

        # Add the number of wins to the wins dictionary for the current winner
        wins[winner] = num_wins

    # Record the number of wins for each player
    winning_record = "<h1 style='color: green;'>============ GAME LEADERBOARD ============</h1><br>"
    winning_record = winning_record + "<h2>Player Name -- Wins "
    winning_record = winning_record + "<p style='color: darkgray;'>===================================</p>"

    # sorted_winners = sorted(wins.items(), key=lambda x: x[1], reverse=True)
    sorted_winners = dict(sorted(wins.items(), key=lambda x: x[1], reverse=True))
    
    for winner, num_wins in sorted_winners.items():
        winning_record = winning_record + "<h2 style='color: darkblue; font-weight: bold'>{} -- {}</h2>".format(winner, num_wins) + \
                                          "<p style='color: darkgray;'> ===================================</p>"

    return Markup(winning_record)

if __name__ == '__main__':
    app.run(port = 8099)