# Snakes and Foxes Game
# Based on the game from Robert Jordan's Wheel of Time
# With help from No Name Publishing
# https://sites.google.com/site/nonamepublishing/Home/products/snakes-foxes 

# The first task is to draw the board as depicted in the above link
# I will be using pygame (for the first time) to draw the board
# I plan to also use pygame to animate the pieces when the time comes
import pygame as pg
import math, csv, random

### The Control ###
# The Control of this relatively simple are left to the main procedure
# The main procedure handles initialization and hosts the game loop
# There are several helper functions used by the main to keep things
# somewhat clean.
def main():
    # Initialize Pygame
    pg.init()
    clock = pg.time.Clock()
    # Use pygame to determine display size
    dispInfo = pg.display.Info()
    width    = int(0.5*dispInfo.current_w)
    height   = int(0.5*dispInfo.current_h)
    # Create the game display at half the full display size
    gameDisp = pg.display.set_mode((width,height))

    # Set Up the Game Board
    # Create 129 empty nodes
    graph = [Node() for i in range(129)]
    # Start by giving node 0 it's special adjacency
    graph[0].Adjs = graph[1:17]
    # Read the CSV File that contains the node attriubtes
    with open('AdjacencyTree.csv', 'rt') as NodeData:
        ND = csv.DictReader(NodeData, delimiter=',')
        for ndData in ND:
            nde = graph[int(ndData['Node'])]
            nde.node = int(ndData['Node'])
            nde.ring = int(ndData['Ring'])
            nde.spok = int(ndData['Spoke'])
            nde.rect = Node2Rect(nde.ring,nde.spok)
            adj1 = int(ndData['Adj1'])
            adj2 = int(ndData['Adj2'])
            adj3 = int(ndData['Adj3'])
            nde.Adjs = (graph[adj1],graph[adj2],graph[adj3])
    
    # Set the tokens
    # Eight snakes placed on the last 8 even nodes
    snakes = [Token(i,"snakes",graph[128-2*i])   for i in range(8)]
    # Eight foxes placed on the last 8 odd nodes
    foxes  = [Token(i, "foxes",graph[128-2*i-1]) for i in range(8)]
    # One player token placed in the center of the board
    player = Token(0,"player",graph[0])
    # Bundle the tokens into a single element
    tokens = [snakes, foxes, player]

    # Draw the game board & tokens
    updateBoard(gameDisp, tokens)
    
    # Player makes an initial 1-move turn to get on the board
    game = True
    pMoves=1
    # Determine eligible spaces
    eli = eligibleNodes(player,pMoves)
    # Highlight eligible spaces
    drawMoves(gameDisp, eli)
    while pMoves:
        clock.tick(30)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pMoves=0
                game=False
            elif event.type == pg.MOUSEBUTTONUP:
                # Check if click was in an eligible node
                click = [c for c in eli if c.rect.collidepoint(event.pos)]
                # Move player token to selected node
                # If the user managed to click more than one node, use 0
                if click:
                    player.moveToken(click[0])
                    pMoves = 0
    
    updateBoard(gameDisp,tokens)

    while game:
        # Every good game loop has this
        clock.tick(30)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game = False

        # Turn Initialization
        Moves = [0,0,0]

        # Dovie'andi se tovya sagain
        rolls = diceRoll()
        # Read the dice
        for roll in rolls:
            Moves[int(roll/2)] = Moves[int(roll/2)] + 1
        # Draw the dice
        drawDice(gameDisp,rolls)

        # Each team takes their turn
        for turn in range(3):
            # turn 0 - snakes
            # turn 1 - foxes
            # turn 2 - player
            if 0 == turn: #Snakes Turn
                # Do Snake Things
                pass
            elif 1 == turn: #Foxes Turn
                # Do Fox things
                pass
            elif 2 == turn: #Player Turn
                # Determine eligible spaces
                el = eligibleNodes(player,pMoves)
                # Highlight eligible spaces
                drawMoves(gameDisp, eli)
                while Moves[turn]:
                    clock.tick(30)
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            Moves[turn]=0
                            game=False
                        elif event.type == pg.MOUSEBUTTONUP:
                            # Check if click was in an eligible node
                            p = event.pos
                            clk = [c for c in el if c.rect.collidepoint(p)]
                            # Move player token to selected node
                            if clk:
                                player.moveToken(clk[0])
                                Moves[turn] = 0
            else:
                print("You broke to turn indicator dummy!")
    pg.quit()

def eligibleNodes(token, moves):
    steps = token.pos.Adjs
    while moves:
        eli = steps
        steps2 = []
        for step in steps:
            steps2.extend(step.Adjs)
        #print(steps2)
        steps=steps2
        moves = moves-1
    return eli

def diceRoll():
    dovie  = random.randrange(6)
    andi   = random.randrange(6)
    se     = random.randrange(6)
    tovya  = random.randrange(6)
    sagain = random.randrange(6)
    pips   = random.randrange(6)
    return (dovie,andi,se,tovya,sagain,pips)

def pathFinder(nodeA, nodeB, plen, Path):
    flen = math.inf
    if nodeA is nodeB:
        return (plen,Path)
    elif nodeB in nodeA.Adjs:
        plen = plen+1
        Path.append(nodeB)
        return (plen,Path)
    else:
        for adj in nodeA.Adjs:
            nlen,nath = pathFinder(adj,nodeB,plen+1,Path)
            if nlen < flen:
                flen = nlen
                nath.append(adj)
                Path = nath
        return (flen,Path)

### The Board ###
# The board is composed of eight concentric circles and 16 'spokes'
# There would only be eight spokes if each passed completely through the
# center of the board, but each spoke ends at the inner-most circle.
# The spokes begin at the outter-most circle. The non-player pieces begin 
# at each of the sixteen spokes on the outter-most circle; alternating 
# snakes and foxes. The player's piece begins inside the inner-most circle.
def drawBoard(disp):
    # Get dimensions of the surface
    w,h = pg.display.get_surface().get_size()
    # Center point of circles is at midpoint of surface
    cx = int(w/2)
    cy = int(h/2)
    # Total Radius is 48% of height
    tr = int(48*h/100)
    # Draw the eight circles
    # Draw outer-most blue circle
    pg.draw.circle(disp, (0,0,255), (cx,cy), tr)
    # Need black fill in between circles
    pg.draw.circle(disp, (0,0,0),   (cx,cy), tr-3)
    # Draw the six interior red & green circles
    for i in range(7,2,-2):
        pg.draw.circle(disp, (255,0,0), (cx,cy), int(i*tr/8))
        pg.draw.circle(disp, (0,0,0),   (cx,cy), int(i*tr/8-3))
        pg.draw.circle(disp, (0,255,0), (cx,cy), int((i-1)*tr/8))
        pg.draw.circle(disp, (0,0,0),   (cx,cy), int((i-1)*tr/8-3))
    # Draw the inner-most blue circle
    pg.draw.circle(disp, (0,0,255), (cx,cy), int(tr/8))
    pg.draw.circle(disp, (0,0,0),   (cx,cy), int(tr/8-3))

    # Draw the spokes all in blue
    # The end points of spoke n are:
    # x1 = cx + tr/8 * cos(pi - n*2pi/17)
    # y1 = cy - tr/8 * sin(pi - n*2pi/17)
    # x2 = cx +   tr * cos(pi - n*2pi/17)
    # y2 = cy -   tr * sin(pi - n*2pi/17)
    for i in range(1,17):
        theta = (7/16)*math.pi - (i-1)*math.pi/8
        x1 = int(cx + (tr/8)*math.cos(theta))
        y1 = int(cy - (tr/8)*math.sin(theta))
        x2 = int(cx +     tr*math.cos(theta))
        y2 = int(cy -     tr*math.sin(theta))
        pg.draw.line(disp,(0,0,255),(x1,y1),(x2,y2),3)
    # Push drawings to display
    pg.display.flip()

# The tokens represent the games various "players" which are the user
# player's purple token, the snakes eight yellow tokens and the foxes
# cyan tokens. In the future the plan is to replace to single colored
# circles with images representative of the token type
def drawTokens(disp, tokens):
    # Separate tokens
    snakes,foxes,player = tokens
    # Draw the snakes in yellow
    for snake in snakes:
        sx,sy = getRealCoords(snake.pos.ring,snake.pos.spok)
        pg.draw.circle(disp, (255,255,0), (sx,sy), 7)
    # Draw the foxes in cyan
    for fox in foxes:
        fx,fy = getRealCoords(fox.pos.ring,fox.pos.spok)
        pg.draw.circle(disp, (0,255,255), (fx,fy), 7)
    # Draw the player in purple
    px,py = getRealCoords(player.pos.ring,player.pos.spok)
    pg.draw.circle(disp,(255,0,255), (px,py), 7)
    # Push drawings to display
    pg.display.flip()

def drawDice(disp, rolls):
    # Get dimensions of the surface
    w,h = pg.display.get_surface().get_size()
    # Total Radius is 48% of height
    tr = int(48*h/100)
    # First Create Six Rect, one for each dice
    # Anchor Points
    # The first three dice have the same x-coords as do the last three
    dx = 0.15*(w/2 - tr)
    dw = int((w/2-tr)-2*dx)
    x1=x2=x3 = int(dx)
    x4=x5=x6 = int(w-dx-dw)
    dh = dw
    dy = int((h - 3*dh)/4)
    y1=y4 = dy
    y2=y5 = 2*dy + dh
    y3=y6 = 3*dy + 2*dh
    die1 = pg.draw.rect(disp,(255,255,255),pg.Rect(x1,y1,dw,dh))
    die2 = pg.draw.rect(disp,(255,255,255),pg.Rect(x2,y2,dw,dh))
    die3 = pg.draw.rect(disp,(255,255,255),pg.Rect(x3,y3,dw,dh))
    die4 = pg.draw.rect(disp,(255,255,255),pg.Rect(x4,y4,dw,dh))
    die5 = pg.draw.rect(disp,(255,255,255),pg.Rect(x5,y5,dw,dh))
    die6 = pg.draw.rect(disp,(255,255,255),pg.Rect(x6,y6,dw,dh))
    dice = [die1,die2,die3,die4,die5,die6]
    #Draw the pips
    pr = int(dh/10) # Pip Radius
    for die,roll in enumerate(rolls):
        roll = roll + 1
        if 1 == roll:
            # Special Case, at rectangle center
            px = dice[die].centerx
            py = dice[die].centery
            pg.draw.circle(disp,(0,0,0),(px,py),pr)
        elif 2 <= roll:
            R = int(dh/4)
            for i in range(roll):
                theta = math.pi/2 - (i/roll)*2*math.pi
                px = R * math.cos(theta)
                py = R * math.sin(theta)
                rpx = int(dice[die].centerx + px)
                rpy = int(dice[die].centery - py)
                pg.draw.circle(disp,(0,0,0),(rpx,rpy),pr)
    pg.display.flip()


def drawMoves(disp, moves):
    for move in moves:
        mx,my = getRealCoords(move.ring,move.spok)
        pg.draw.circle(disp,(255,255,255), (mx,my), 4)
    pg.display.flip()

def highlightNodes(disp,nodes):
    for node in nodes:
        hx,hy = getRealCoords(node.ring,node.spok)
        pg.draw.circle(disp,(128,0,255),(hx,hy), 4)
    pg.display.flip()

def updateBoard(disp,tokens):
    # Draw a fresh screen
    pg.display.get_surface().fill((0,0,0))
    pg.display.flip()
    # Re-draw the board
    drawBoard(disp)
    # Re-draw the tokens in their new state
    drawTokens(disp,tokens)


# Helper function that yields the surface coordinates of a node
# based on the pre-determined board position and size
def getRealCoords(ring,spok):
    # Get surface dimensions
    w,h = pg.display.get_surface().get_size()
    # Circle center is at surface midpoint
    cx = int(w/2)
    cy = int(h/2)
    # Total radius is 48% surface height
    tr = int(48*h/100)
    # Angle
    theta = 7*math.pi/16 - (spok-1)*math.pi/8
    sx = ring * (tr/8)*math.cos(theta)
    sy = ring * (tr/8)*math.sin(theta)
    rx = int(cx + sx)
    ry = int(cy - sy)
    return (rx,ry)

def Node2Rect(ring,spok):
    nx,ny = getRealCoords(ring,spok)
    return pg.Rect(nx-5,ny-5,10,10)

### The Graph ###
# It is one thing to draw the board, but as of yet this board has no
# representation for the program to use. To give the program a 
# useful representation of the board, I will create a Node class that
# represents the intersections of rings and spokes. Links are implicit
# in that they all have uniform cost and each node has knowledge of the
# nodes that can be reached in one move. This Node/Link approach will
# allow me to use graph algorithms to find shortest paths etc...
#
# Regarding Numbering:
# Each ring is numbered such that the inner-most ring is ring 1
# and the outer-most ring is ring 8. (Ring 0 is the center point)
# Furthermore, the spokes are numbered such that Spoke 1 is at "1 o'clock"
# and Spoke 16 is at "11 o'clock" (only spoke 1 is at the "same time")
# There are 16 spokes so the spokes do not line up with the clock exactly
# Spoke 0 also corresponds to the center-point
# The nodes are numbered such that Node 1 is at Ring 1, Spoke 1 and
# ascending in "Spoke Major Order", e.g. Node 2 is Ring 1, Spoke 2,
# Node 17 is Ring 2, Spoke 1, and Node 41 is Ring 3, Spoke 9
# Node 0, Ring 0, and Spoke 0 are unique and represent the center point.
class Node:
    # Adjacency can not be completed until all nodes are instantiated
    # Therefore, we will instantiate each Node empty at first, and
    # allow the graph class to assign attribute to each node
    def __init__(self):
        self.node = 0 # Node ID
        self.ring = 0 # Ring Number of intersection (0 is center point)
        self.spok = 0 # Position of node relative to center point (y)
        self.Adjs = None  # Nodes that can be attained from this node
        self.rect = None  # Pygame Rect object for clickedness
        self.ocpy = False # Is there a token on this node?

### The Tokens ###
# To represent the game pieces I will create a Token Class. This class
# will have the necessary information to distinguish between the types
# of pieces and to locate the piece on the board
class Token:
    def __init__(self,tid,typ,pos):
        self.id=tid
        self.typ=typ # Snake, Fox, or Player
        self.pos=pos # Node on which the token sits
        self.pos.ocpy=True

    def moveToken(self,node):
        # First, unoccupy the current position
        self.pos.ocpy=False
        # Next, take the new node
        self.pos=node
        # Finally, occupy the new node
        self.pos.ocpy=True

main()