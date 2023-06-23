import random
import numpy as np

# Load the embeddings, strip leading underscore
embeddings = np.load('embeddings.npz')
embeddings = {word[1:].replace('_',' ') :embeddings[word] for word in embeddings.files}

def get_embedding(word):
    word = word.lower().strip()
    try:
        return embeddings[word]
    except KeyError as e:
        raise ValueError(f"unknown word {word}") from e


def compute_score(n, dists, closest_wrong):
    """
    Desired properties:
     - higher the closer the words are
     - higher the more guesses
     - higher the further the gap between the furthest guess one
    """
    gap = closest_wrong - np.max(dists)
    
    return np.sqrt(n) - np.mean(dists) + 1.5*gap


def give_clue(our_cards, not_our_cards, all_words):
    """
    Function for the spymaster
    """
    # Determine which guesses are legal to give.
    # We're going off of "does not contain any tile as a substring"
    legal_clues = [
        clue 
        for clue in embeddings 
        if not any(clue.count(word.replace(' ','_'))>0 for word in all_words)
    ]
    
    print("Number of legal clues:", len(legal_clues))
    
    # Find distances for each pair (clue, tile)
    clues_embedding = np.array([
        get_embedding(word) for word in legal_clues
    ])
    our_cards_embedding = np.array([
        get_embedding(word) for word in our_cards
    ])
    not_our_cards_embedding = np.array([
        get_embedding(word) for word in not_our_cards
    ])
    
    # Compute the distances
    our_distances = np.linalg.norm(
        clues_embedding[:,None,:] - our_cards_embedding[None,:,:], axis=2
    )
    not_our_distances = np.linalg.norm(
        clues_embedding[:,None,:] - not_our_cards_embedding[None,:,:], axis=2
    )
    
    
    best_clue = ("", 0)
    best_score = -np.inf
    for clue, our_dists, not_dists in zip(legal_clues, our_distances, not_our_distances):
        # Find the closest wrong word
        closest_wrong = np.min(not_dists)
        
        too_far = our_dists >= closest_wrong
        ok_cards = ~too_far
        max_num_ok = np.sum(ok_cards)
        
        if not np.any(ok_cards):
            # Skip this word
            #continue
            pass
            
        # Otherwise, compute a score
        our_dists = np.sort(our_dists)
        
        for n in range(1, len(our_cards)):
            score = compute_score(n, our_dists[:n], closest_wrong)
            if max_num_ok < n:
                score -= 5
            if score > best_score:
                best_clue = (clue, n)
                best_score = score
    
    if best_clue == ("", 0):
        raise Exception("Failed to find any clues")
    
    return best_clue


def give_me_a_clue(reds_turn, all_words, red_list, blue_list):
    if reds_turn: # ------------------------------------------------------- check whose turn it is
        our_words = red_list
    else:
        our_words = blue_list
    
    not_our_words = [word for word in all_words if not word in our_words]

    return give_clue(our_words, not_our_words, all_words)


########################################################################################################

def example1():
    red_list = ['red1', 'red2', 'red3']
    blue_list = ['blue1', 'blue2', 'blue3']
    yellow_list = ['yellow1', 'yellow2', 'yellow3']
    DEATH = 'death'
    all_words = red_list+blue_list+yellow_list+[DEATH]

    return all_words, red_list, blue_list, yellow_list, DEATH


def example2():
    red_list = ['bond', 'apple', 'night', 'plot', 'mole', 'sink', 'chick', 'check']
    blue_list = ['crash', 'fly', 'racket', 'america', 'atlantis', 'mine', 'cast', 'bear', 'bar']
    yellow_list = ['cook', 'dance', 'maple', 'england', 'school', 'pin', 'princess']
    DEATH = 'opera'

    all_words = red_list+blue_list+yellow_list+[DEATH]
    random.shuffle(all_words)

    return all_words, red_list, blue_list, yellow_list, DEATH

########################################################################################################



def make_list():
    word_list = [] # --------------------- new list!
    addingwords = True

    print('Enter DONE when finished')
    while addingwords == True: # --------------- while I want to add words
        word = input("WORD: ")

        if word == "DONE": # ------------- stop adding words
            addingwords = False
        else:
            word_list.append(word) # ----- add words

    return word_list

def setup():
    """
    This function makes the team word lists and a list of all the words :)
    """
    print('\n\nLET\'S SET UP CODENAMES!')
    
    print('\nEnter in words for RED team.')
    red_list = make_list() # --------------------------------------- make my lists
    print('RED LIST: ',red_list)

    print('\nEnter in words for BLUE team.')
    blue_list = make_list()
    print('BLUE LIST: ',blue_list)

    print('\nEnter in words for YELLOW team.')
    yellow_list = make_list()
    print('YELLOW LIST: ',yellow_list)

    DEATH = input('\nEnter in the ASSASSIN WORD: ') # -------------------------------- add in the death word

    all_words = red_list+blue_list+yellow_list+[DEATH] # ----------- list of ALL words
    random.shuffle(all_words) # ------------------------------------ shuffle all my words

    print('\nYou have set up code names!')

    return all_words, red_list, blue_list, yellow_list, DEATH


def guess_it(myguess, reds_turn):
    stop_turn = True
    
    if myguess == 'DONE':
        print(' -- done guessing -- ')
        return True, False 
    
    if myguess == 'QUIT':
        print('\n *** QUITTING GAME *** \n')
        return True, True

    elif myguess in all_words: # ------------------------------------ check if word is valid
        all_words.remove(myguess)
        
        if myguess in red_list: # ----------------------------------- check red list
            print(' -- Red Word -- ')
            red_list.remove(myguess)
            if reds_turn == True: # --------------------------------- if red list on red team, do not stop turn
                stop_turn = False 
            
        elif myguess in blue_list: # --------------------------------- check blue list
            print(' -- Blue Word -- ')
            blue_list.remove(myguess)
            if reds_turn == False:
                stop_turn = False
            
        elif myguess in yellow_list: # ------------------------------- check yellow list
            print(' -- Yellow Word -- ')
            yellow_list.remove(myguess)
        
    else:
        print(' -- invalid entry. try again. -- ') # ----------------- if invalid, guess again
        return False, False

    game_over = check_game(myguess)
    return stop_turn, game_over


def check_game(myguess):
    if len(red_list) == 0: # ----------------------------------------- check if red won
        print('\n**********************************')
        print('***** RED TEAM WINS! WHOOOOO *****')
        print('**********************************\n')
        return True
    elif len(blue_list) == 0: # --------------------------------------- check if blue won
        print('\n***************************')
        print('***** BLUE TEAM WINS! *****')
        print('***************************\n')
        return True
    elif myguess == DEATH:  # ----------------------------------------- check if DEATH WORD was chosen
        print('\n************************************************')
        print('***** YOU LOSE. HAHAHA. SUCKS TO SUCK NERD *****')
        print('************************************************\n')
        return True
    else:  # ---------------------------------------------------------- otherwise, game is not over
        return False


def turn(clue, num_cards, reds_turn):
    print('\n--- CLUE for ',num_cards,':',clue, ' --- ') # ----------------------------------------------- present the clue
    stop_turn = False

    while stop_turn == False: # ------------------------------------------- keep guessing until the turn is over
        print('\nremaining words:',all_words)
        myguess = input('guess:\t')
        stop_turn, game_over = guess_it(myguess, reds_turn)

        if game_over == True: # ------------------------------------------- end if game is over
            return  True

    return False

            



### PLAY GAME


# all_words, red_list, blue_list, yellow_list, DEATH = setup()
#all_words, red_list, blue_list, yellow_list, DEATH = example1() # ----- If you want to test your code, but don't want to enter in words every time
all_words, red_list, blue_list, yellow_list, DEATH = example2()

print('\n\n##############################')
print('### LET\'S PLAY CODE NAMES! ###')
print('##############################')

print('\n(type DONE when you\'re done guessing, QUIT to end the game)')

if len(red_list) > len(blue_list):
    reds_turn = True
else:
    reds_turn = False

game_over = False
while game_over == False:
    if reds_turn == True:
        print('\n\n**********\nRED\'S TURN\n**********')
    else:
        print('\n\n***********\nBLUE\'S TURN\n***********')

    clue, num_cards = give_me_a_clue(reds_turn, all_words, red_list, blue_list)

    game_over = turn(clue, num_cards, reds_turn)
    reds_turn = not reds_turn







