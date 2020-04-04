
assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'
cols_reverse= cols[::-1]

def cross(a, b):
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

d1_units = [[rows[n]+cols[n] for n in range(len(rows))]]
d2_units = [[rows[n]+cols_reverse[n] for n in range(len(rows))]]

# For diagonal sudoku

yes_diagonal = 1 # Set this yes_diagonal = 0 for non-diagonal sudoku
if yes_diagonal == 1:
    unitlist = row_units + column_units + square_units + d1_units + d2_units
else:
    unitlist = row_units + column_units + square_units
	

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    possible_twins = [box for box in values.keys() if len(values[box]) == 2]
	
    lst_nakedtwins = [[box1,box2] for box1 in possible_twins \
                      for box2 in peers[box1] \
                      if set(values[box1])==set(values[box2])]
					  
    for i in range(len(lst_nakedtwins)):
        box1 = lst_nakedtwins[i][0]
        box2 = lst_nakedtwins[i][1]
        peers_1 = set(peers[box1])
        peers_2 = set(peers[box2])
        peers_int = peers_1 & peers_2
        for peer_vals in peers_int:
            if len(values[peer_vals])>2:
                for rem_val in values[box1]:
                    values = assign_value(values, peer_vals, values[peer_vals].replace(rem_val,'')) 
    return values

	
'''
def cross(A, B):
    "Cross product of elements in A and elements in B."
    pass
'''

def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '123456789' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '123456789' if it is empty.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))


def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

	
def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,'')) 
            # values[peer] = values[peer].replace(digit,'')
    return values


def only_choice(values):

    '''Write a function that will take as an input, the sudoku in dictionary form,
    run through all the units, applying the only choice technique,
    and return the resulting sudoku in dictionary form.'''
   
    for unit in unitlist:
        for digit in '123456789':
            dspots = [box for box in unit if digit in values[box]]
            if len(dspots) == 1:
                values[dspots[0]] = digit
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    '''Using depth-first search and propagation, create a search tree and solve the sudoku.'''
       
    #Using depth-first search and propagation, try all possible values.
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    values = search(values)

    return values


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')


    # References:
    # Udacity AIND lectures
    #http://norvig.com/sudoku.html
    #http://stackoverflow.com/
    #https://docs.python.org/3/