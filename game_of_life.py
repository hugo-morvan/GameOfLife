from mimetypes import init
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import pandas as pd
import numpy as np
import time
import datetime
from tqdm import trange

"""
These rules, which compare the behavior of the automaton to real life, can be condensed into the following:

Any live cell with two or three live neighbours survives.
Any dead cell with three live neighbours becomes a live cell.
All other live cells die in the next generation. Similarly, all other dead cells stay dead.
"""
# Grid refers to the list of lists containing data
# Plot refers to the visual plot of that data


def updateGrid( grid, rowCt, colCt ):
    
    live_ct, death_ct = 0, 0 # how many total live cells in the grid and how many cells died
        
    rows, cols = grid.shape[0], grid.shape[1] # get the size of the grid
    dr, dc = [1, 0, -1, 1, -1, 1, 0, -1], [-1, -1, -1, 0, 0, 1, 1, 1] # for checking neighboring cells
    rUpdate, cUpdate = [], []  # store which cells we need to flip in this update

    for r in range(rows):
        check = False           # Only check rows where we can potentially make a change
        if rowCt[r]>0:          #   if this row has at least one live cell, we can make a change
            check = True
        if r>0:
            if rowCt[r-1]>0:    #   if the row to the left of this row has at least one live, check this row
                check = True
        if r<(rows-1):
            if rowCt[r+1]>0:    #   if the row to the right of this row has at least one live, check this row
                check = True
                
        if check:                       # if we need to check this row
            nbrCt = 0                   # initialize how many neigbors we have
            #print("\nr:",r)
            for i in range(3, len(dr)): # check all in-bounds neighbors
                newR = r+dr[i]          
                cc = dc[i]
                #print("Checking r:",newR,"c:",cc)
                if newR >= 0 and newR < rows:
                    nbrCt += grid[newR][cc]
                    #print("Valid, adding",grid[newR][cc])
            #print("c: 0 nbrCt:",nbrCt)
            checkCol = True             # Initialize the variable for if we should check this column
            
            for c in range(cols):
                updateNbr = False           # check if we just skipped some columns
                if checkCol == False:
                    updateNbr = True
                else:
                    checkCol = False
                    
                if colCt[c]>0:
                    checkCol = True
                if c>0:
                    if colCt[c-1]>0:
                        checkCol = True
                if c<(cols-1):
                    if colCt[c+1]>0:
                        checkCol = True
                
                if checkCol:
                    if updateNbr:
                        nbrCt = grid[r][c] - grid[r][c-1]
                        for i in range(5):
                            newR = r+dr[i]
                            newC = c+dc[i]
                            if newR>=0 and newR<rows and newC>=0 and newC<cols:
                                nbrCt += grid[newR][newC]
                    
                    if c>0:
                        nbrCt -= grid[r][c]
                        nbrCt += grid[r][c-1]
                        for i in range(5, len(dr)):
                            newR = r+dr[i]
                            newC = c+dc[i]
                            if newR>=0 and newR<rows and newC>=0 and newC<cols:
                                nbrCt += grid[newR][newC]
                        #print("c:",c,"nbrCt:",nbrCt)
                    if grid[r][c] == 0:
                        if nbrCt == 3:
                            rUpdate.append(r)
                            cUpdate.append(c)
                            live_ct += 1
                            rowCt[r] += 1
                            colCt[c] += 1
                    else:
                        if nbrCt < 2 or nbrCt > 3:
                            rUpdate.append(r)
                            cUpdate.append(c)
                            death_ct += 1
                            rowCt[r] -= 1
                            colCt[c] -= 1
                        else:
                            live_ct += 1
                    if c>0:
                        for i in range(3):
                            newR = r+dr[i]
                            newC = c+dc[i]
                            #print("\nChecking r:",newR,"c:",newC)
                            if newR>=0 and newR<rows and newC>=0 and newC<cols:
                                nbrCt -= grid[newR][newC]
                                #print("valid, subtracting",grid[newR][newC])
    
    for r, c in zip(rUpdate, cUpdate):
            if grid[r][c] == 0:
                grid[r][c] = 1
            else:
                grid[r][c] = 0
                

    return grid, live_ct, death_ct, rowCt, colCt

def simulateGame( grid, time_steps, live_init ):
    # Initialize plot
    x, y = [], []
    for row in range(grid.shape[0]):
        for col in range(grid.shape[1]):
            if grid[row][col] == 1:
                x.append(col)
                y.append(row)
    
    plt.ion()
    fig, ax = plt.subplots()
    gridPlt = ax.scatter(x, y, marker='x', color='b')
    plt.xticks(ticks=[])
    plt.yticks(ticks=[])
    plt.xlim(-1, grid.shape[0])
    plt.ylim(grid.shape[1], -1)
    plt.draw()

    # Initialize row and column counts
    rCt, cCt = np.zeros(grid.shape[0]), np.zeros(grid.shape[1])
    for row in range(grid.shape[0]):
        for col in range(grid.shape[1]):
            if grid[row][col] == 1:
                rCt[row] += 1
                cCt[col] += 1

     #beginning of the simulation :
    live_ct = live_init
    death_ct = 0

    prev = -1
    start_time = time.time()
    
    for step in trange(time_steps):
        grid, live_update, death_update, rCt, cCt = updateGrid( grid, rCt, cCt )
        live_ct += live_update
        death_ct += death_update

        #Update plot
        x, y = [], []
        for row in range(grid.shape[0]):
            for col in range(grid.shape[1]):
                if grid[row][col] == 1:
                    x.append(col)
                    y.append(row)

        gridPlt.set_offsets(np.c_[x,y])
        fig.canvas.draw_idle()
        plt.pause(0.05)
    
        if (death_update == 0 and live_update == prev) or live_update == 0: #means no movement, still life, therefore we can stop the simulation
            live_ct += live_update*(time_steps-step) #live_ct is updated to predict the rest of the simulation that is stopped
            break
    
    #end of simulation, displays of results
    end_time = time.time()
    delta_t = (end_time - start_time)
    print('Start time:', datetime.datetime.fromtimestamp(start_time).strftime('%c'))
    print('End time:', datetime.datetime.fromtimestamp(end_time).strftime('%c'))
    print('Elapsed time:' , delta_t*1000 , 'ms')
    print('Number of frames processed:', time_steps)
    print('Total living cells: ', live_ct)
    print('Total death cells: ' , death_ct)

    print('Average Frame Per Second (FPS):', time_steps/delta_t)

"""
Your script will begin by offering the user to select from the following initial states:
•blinker
•glider gun
•random (cells are set to living with some percentage of probability).
•another pattern which interests you

Your script will then ask for a grid size (grid will always be square so just ask for a single number).

Finally, your script will ask the user how many time steps to run the simulation for.
When you script has finished, some statistics will be displayed.  
You will show the start date/time of thesimulation, the end date/time of the simulation, the number of milliseconds elapsed, 
the number of frames processed, the total number of living cells during processing (just sum up the number of living cells
across all timesteps of the simulation), 
and the number of cells that died across all timesteps of thesimulation.

"""
#TODO: ERROR CODE FOR INPUT (ONLY VALID INPUT - GRID SIZE > 3, ETC.)

def initGame():
    #initialisation
    init_state = input('Select initial state: [b]linker , [g]lider gun, [r]andom or [i]nfinite : ')
    while init_state not in ['b', 'g', 'r', 'i']:
        init_state = input('Please enter a valid state : ')
    
    grid_size = int(input('Enter grid size : '))
    if init_state == 'g':
        while grid_size < 36:
            grid_size = int(input('Grid size must be at least size 36 for this type. Enter new size: '))
    elif init_state == 'b':
        while grid_size <3:
            grid_size = int(input('Grid size must be at least size 3 for this type. Enter new size: '))
    elif init_state == 'r':
        while grid_size < 1:
            grid_size = int(input('Grid size must be at least size 1 for this type. Enter new size: '))
    elif init_state == 'i':
        while grid_size < 5:
            grid_size = int(input('Grid size must be at least size 5 for this type. Enter new size: '))

    time_steps = int(input('Enter the number of time steps to run the simulation for : '))
    while time_steps < 0:
        time_steps = int(input('Please enter a value of time steps greater than 0 : '))
        
    total_live_ct = 0


    grid = np.zeros((grid_size, grid_size))
    mid = int(grid_size/2)
    #grid[row][column]
    #top left = grid[0][0]
    #directly below top left = grid[1][0]
    if init_state == 'b':
        # O X O
        # O X O
        # O X O
        grid[mid][mid] = 1
        grid[mid+1][mid] = 1
        grid[mid-1][mid] = 1
        total_live_ct = 3

    elif init_state == 'g':
        #Gosper Glider gun
        grid[5][1]=1
        grid[5][2]=1
        grid[6][1]=1
        grid[6][2]=1

        grid[5][11]=1
        grid[6][11]=1
        grid[7][11]=1

        grid[4][12]=1
        grid[8][12]=1

        grid[3][13]=1
        grid[9][13]=1
        grid[3][14]=1
        grid[9][14]=1

        grid[6][15]=1

        grid[4][16]=1
        grid[8][16]=1

        grid[5][17] = 1
        grid[6][17] = 1
        grid[7][17] = 1

        grid[6][18] = 1

        grid[3][22] = 1
        grid[4][22] = 1
        grid[5][22] = 1
        grid[3][21] = 1
        grid[4][21] = 1
        grid[5][21] = 1
        
        grid[2][23] = 1
        grid[6][23] = 1

        grid[1][25] = 1
        grid[2][25] = 1
        grid[6][25] = 1
        grid[7][25] = 1

        grid[3][35] = 1
        grid[4][35] = 1
        grid[3][36] = 1
        grid[4][36] = 1

        total_live_ct = 35

    elif init_state == 'r':
        #randomised grid
        grid = np.random.randint(2, size=(grid_size, grid_size))
        total_live_ct = np.sum(grid)

    elif init_state == 'i' and grid_size>=5 :
        # X X X O X
        # X O O O O
        # O O O X X
        # O X X O X
        # X O X O X
        grid[mid-2][mid-2] = 1
        grid[mid-2][mid-1] = 1
        grid[mid-2][mid] = 1
        grid[mid-2][mid+2] = 1
        grid[mid-1][mid-2] = 1
        grid[mid][mid+2] = 1
        grid[mid][mid+1] = 1
        grid[mid+1][mid-1] = 1
        grid[mid+1][mid] = 1
        grid[mid+1][mid+2] = 1
        grid[mid+2][mid-2] = 1
        grid[mid+2][mid] = 1
        grid[mid+2][mid+2] = 1
        total_live_ct = 13
    elif init_state == 'i' and grid_size < 5 :
        print('Grid size too small for this input')

    simulateGame(grid, time_steps, total_live_ct)
    
initGame()
