# Snakes and Foxes Game
# Based on the game from Robert Jordan's Wheel of Time
# With help from No Name Publishing
# https://sites.google.com/site/nonamepublishing/Home/products/snakes-foxes 

# The first task is to draw the board as depicted in the above link
# I will be using pygame (for the first time) to draw the board
# I plan to also use pygame to animate the pieces when the time comes
import pygame as pg
import math

### The Board ###
# The board is composed of eight concentric circles and 16 'spokes'
# There would only be eight spokes if each passed completely through the
# center of the board, but each spoke ends at the inner-most circle.
# The spokes begin at the outter-most circle. The non-player pieces begin 
# at each of the sixteen spokes on the outter-most circle; alternating
# snakes and foxes. The player's piece begins inside the inner-most circle.
def drawBoard(gd, width, height):
    # Draw the eight circles
    # Center point is midpoint
    cx = int(width/2)
    cy = int(height/2)
    # Total Radius is 45% of height
    tr = int(48*height/100)
    # Draw outer-most blue circle
    pg.draw.circle(gd, (0,0,255), (cx,cy), tr)
    pg.draw.circle(gd, (0,0,0),   (cx,cy), tr-3)
    # Draw the interior red & green circles
    for i in range(7,2,-2):
        pg.draw.circle(gd, (255,0,0), (cx,cy), int(i*tr/8))
        pg.draw.circle(gd, (0,0,0),   (cx,cy), int(i*tr/8-3))
        pg.draw.circle(gd, (0,255,0), (cx,cy), int((i-1)*tr/8))
        pg.draw.circle(gd, (0,0,0),   (cx,cy), int((i-1)*tr/8-3))
    # Draw the inner-most blue circle
    pg.draw.circle(gd, (0,0,255), (cx,cy), int(tr/8))
    pg.draw.circle(gd, (0,0,0),   (cx,cy), int(tr/8-3))

    # Draw the spokes all in blue
    # The end points of spoke n are:
    # x1 = cx + tr/8 * cos(pi - n*2pi/17)
    # y1 = cy - tr/8 * sin(pi - n*2pi/17)
    # x2 = cx +   tr * cos(pi - n*2pi/17)
    # y2 = cy -   tr * sin(pi - n*2pi/17)
    for i in range(1,17):
        theta = (7/16)*math.pi - (i-1)*2*math.pi/16
        x1 = int(cx + (tr/8)*math.cos(theta))
        y1 = int(cy - (tr/8)*math.sin(theta))
        x2 = int(cx +     tr*math.cos(theta))
        y2 = int(cy -     tr*math.sin(theta))
        pg.draw.line(gd,(0,0,255),(x1,y1),(x2,y2),3)

    pg.display.flip()

def main():

    pg.init()

    dispInfo = pg.display.Info()
    width    = int(0.5*dispInfo.current_w)
    height   = int(0.5*dispInfo.current_h)
    gameDisp = pg.display.set_mode((width,height))

    drawBoard(gameDisp,width,height)

    game = True
    while game:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game = False

    pg.quit()

main()