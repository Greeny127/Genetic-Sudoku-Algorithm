from sudoku import Sudoku
import tkinter.font as font
import tkinter as tk
import threading
import multiprocessing
import random
import matplotlib.pyplot as plt
import copy


class App():
    def __init__(self, root, board=None):
        '''
        Initialisize all constants and render window
        '''
        self.root = root  # Initliaise for tkinter

        # Constants for the algorithm
        self.PUZZLE = Sudoku(2, 2).difficulty(0.99)
        self.BOARD = board
        if board == None:
            self.BOARD = self.PUZZLE.board  # row by row

        self.SOLUTION = self.PUZZLE.solve().board
        self.POPULATION_SIZE = 100
        self.SURVIVAL_SIZE = 20

        self.LOCKED = self.get_locked(self.BOARD)  # An array of locked numbers
        self.ALLSCORES = []
        self.ALLELITESCORES = []
        self.y = []

        self.create_cells()  # render the tkinter screen

        # Start a secondary thread for the algorithm to run alongside the window
        t2 = threading.Thread(target=self.start, kwargs={
                              "selection_m": "not_rank"})

        if board != None:
            t2 = threading.Thread(target=self.start)
        t2.start()

    def create_cells(self):
        '''
        Create a window containing the sudoku, score and generation
        '''
        self.cells = []
        self.score = []
        self.generation = []

        my_font = font.Font(size=15, weight="bold")
        for i in range(4):
            row = []
            for j in range(4):
                # if the cell is locked number
                if self.BOARD[i][j] != None:
                    color = "light green"
                    forecolor = "black"

                # if changeable cell
                else:
                    forecolor = "black"
                    color = "white"

                button = tk.Button(
                    text=self.BOARD[i][j], width=10, height=5, background=color, foreground=forecolor, font=my_font)
                button.grid(row=i, column=j)

                row.append(button)
            self.cells.append(row)

        self.score = tk.Label(text="0", font=my_font)
        self.score.grid(row=0, column=6)
        self.generation = tk.Label(text="100", font=my_font)
        self.generation.grid(row=0, column=9)

    def get_locked(self, board):
        '''
        To store the current locked numbers' index

        Args:
            board (array): The unsolved, default sudoku grid

        Returns:
            array: List of locked numbers' index relative to the default grid
        '''
        indicess = []
        count_digit = 0
        for row in board:
            temp = []
            for digit in row:
                if digit != None:
                    temp.append(count_digit)

                count_digit += 1

            indicess.append(temp)
            count_digit = 0

        return indicess

    def create_starting_population(self, limit):
        '''
        Creates the first population with random combinations

        Args:
            limit (int): The limit for how many combination to generate

        Returns:
            array: All the generated combinations
        '''
        final_population = []
        generated = False
        cycle = 0

        while not generated:
            board = copy.deepcopy(self.BOARD)
            count_row = 0
            count_digit = 0

            if cycle == limit:
                generated = True

            for row in board:
                for digit in row:
                    if digit == None:
                        created = False

                        while not created:
                            new_digit = random.randint(1, 4)

                            if new_digit not in row:
                                board[count_row][count_digit] = new_digit
                                created = True

                    count_digit += 1

                count_row += 1
                count_digit = 0

            final_population.append(board)
            cycle += 1

        return final_population

    def find_fitness(self, combination):
        '''
        Calculates fitness score for a combination by counting duplicate numbers in every grid, row and column. The higher the score, the more duplicates

        Args:
            combination (array): possible solution to the sudoku

        Returns:
            int: The final score calculated
        '''
        final_score = 0  # score increases as duplicates increases, lesser is better, 0 is solved

        # ROW
        for row in combination:
            if len(row) > len(set(row)):
                duplicates = (len(row) - len(set(row)))
                final_score += duplicates

        # COLUMN
        for digit in range(4):
            col = []
            for column in range(4):
                col.append(combination[column][digit])

            if len(col) > len(set(col)):
                duplicates = (len(col) - len(set(col)))
                final_score += duplicates

            col = []

        # GRID
        grid1 = [combination[0][0], combination[0]
                 [1], combination[1][0], combination[1][1]]
        grid3 = [combination[2][0], combination[2]
                 [1], combination[3][0], combination[3][1]]
        grid2 = [combination[0][2], combination[0]
                 [3], combination[1][2], combination[1][3]]
        grid4 = [combination[2][2], combination[2]
                 [3], combination[3][2], combination[3][3]]
        grids = [grid1, grid2, grid3, grid4]

        for grid in grids:
            if len(grid) > len(set(grid)):
                duplicates = (len(grid) - len(set(grid)))
                final_score += duplicates

        return final_score

    def rank_population(self, population):
        '''
        Ranks the entire population

        Args:
            population (array): All the combinations created of the population

        Returns:
            array: Each item contains the rank and index of combintation. For every combination in the population
        '''
        scores = []
        index = 0
        for combi in population:
            scores.append([self.find_fitness(combi), index])
            index += 1

        # Sort the scores in ascending order of score
        scores = sorted(scores, key=lambda x: x[0], reverse=True)
        return scores

    def tournament_selection_gpt(self, population, limit):
        selected = []

        for _ in range(min(limit, len(population))):
            comb1 = random.choice(population)
            comb2 = random.choice([c for c in population if c != comb1])

            point1 = self.find_fitness(comb1)
            point2 = self.find_fitness(comb2)

            selected.append(comb1 if point2 > point1 else comb2)

        return selected

    def tournament_selection(self, population, limit):
        selected = []
        done = False
        cycle = 0

        while not done:
            if cycle == limit:
                done = True

            comb1 = random.choice(population)
            comb2 = random.choice([c for c in population if c != comb1])

            point1 = self.find_fitness(comb1)
            point2 = self.find_fitness(comb2)

            if point2 > point1:
                selected.append(comb1)
                population.remove(comb1)

            if point1 > point2:
                selected.append(comb2)
                population.remove(comb2)

            cycle += 1

        return selected

    def selection(self, population, ranked, limit):
        '''
        Uses Rank Based Selection to select the combinations for the next generation

        Args:
            population (array): Contains all the combinations of the current generation
            ranked (array): Contains the list of ranks and index of each ranked combination
            limit (int): The limit to how many can be selected from population

        Returns:
            array: The list of selected combinations
        '''
        selected = []
        roulette = []
        final_selected = []

        # Create the roulette with the probability equal to rank
        for item in ranked:
            for i in range(item[1]):
                roulette.append(item)

        for cycle in range(limit):
            selected.append(random.choice(roulette))

        for item in selected:
            final_selected.append(population[item[1]])

        return final_selected

    def crossover(self, combination1, combination2, t=1):
        '''
        Combines two combinations to create new combinations

        Args:
            combination1 (array): parent 1
            combination2 (array): parent 2

        Returns:
            array: The two new children formed from the crossover
        '''
        child1 = copy.deepcopy(combination1)
        child2 = copy.deepcopy(combination2)

        chance = random.randint(1, 4)

        # Grid crossover
        if chance == 1:
            child1[0][0], child1[0][1], child1[1][0], child1[1][1] = combination2[0][0], combination2[0][1], combination2[1][0], combination2[1][1]
            child2[0][0], child2[0][1], child2[1][0], child2[1][1] = combination1[0][0], combination1[0][1], combination1[1][0], combination1[1][1]

            child1[2][0], child1[2][1], child1[3][0], child1[3][1] = combination2[2][0], combination2[2][1], combination2[3][0], combination2[3][1]
            child2[2][0], child2[2][1], child2[3][0], child2[3][1] = combination1[2][0], combination1[2][1], combination1[3][0], combination1[3][1]

        # Grid crossover
        if chance == 2:
            child1[0][2], child1[0][3], child1[1][2], child1[1][3] = combination2[0][2], combination2[0][3], combination2[1][2], combination2[1][3]
            child2[0][2], child2[0][3], child2[1][2], child2[1][3] = combination1[0][2], combination1[0][3], combination1[1][2], combination1[1][3]

            child1[2][2], child1[2][3], child1[3][2], child1[3][3] = combination2[2][2], combination2[2][3], combination2[3][2], combination2[3][3]
            child2[2][2], child2[2][3], child2[3][2], child2[3][3] = combination1[2][2], combination1[2][3], combination1[3][2], combination1[3][3]

        # Column crossover
        if chance == 3:
            child1[0][0], child1[1][0], child1[2][0], child1[3][0] = combination2[0][0], combination2[1][0], combination2[2][0], combination2[3][0]
            child2[0][0], child2[1][0], child2[2][0], child2[3][0] = combination1[0][0], combination1[1][0], combination1[2][0], combination1[3][0]

            child1[0][2], child1[1][2], child1[2][2], child1[3][2] = combination2[0][2], combination2[1][2], combination2[2][2], combination2[3][2]
            child2[0][2], child2[1][2], child2[2][2], child2[3][2] = combination1[0][2], combination1[1][2], combination1[2][2], combination1[3][2]

        # Column crossover
        if chance == 4:
            child1[0][1], child1[1][1], child1[2][1], child1[3][1] = combination2[0][1], combination2[1][1], combination2[2][1], combination2[3][1]
            child2[0][1], child2[1][1], child2[2][1], child2[3][1] = combination1[0][1], combination1[1][1], combination1[2][1], combination1[3][1]

            child1[0][3], child1[1][3], child1[2][3], child1[3][3] = combination2[0][3], combination2[1][3], combination2[2][3], combination2[3][3]
            child2[0][3], child2[1][3], child2[2][3], child2[3][3] = combination1[0][3], combination1[1][3], combination1[2][3], combination1[3][3]

        return child1, child2

    def shuffle(self, lst, locked_indices):
        '''
        Shuffles the order of an array while keeping specific elemts locked in position

        Args:
            lst (array): parent array
            locked_indices (array): positions of locked elements

        Returns:
            array: the new shuffled array
        '''

        # Shuffle the unlocked elements
        unlocked_elements = [lst[i]
                             for i in range(len(lst)) if i not in locked_indices]
        random.shuffle(unlocked_elements)

        # Combine the shuffled unlocked elements with the locked elements
        shuffled_lst = [lst[i] if i in locked_indices else unlocked_elements.pop(
            0) for i in range(len(lst))]

        return shuffled_lst

    def mutation(self, combi, rate, totalrate):
        '''
        Mutates combination to introduce more diversity

        Args:
            combi (array): combination
            rate (integer): rate of mutaiton
            totalrate (integer): rate of mutation

        Returns:
            array: The new mutated or non mutated array
        '''
        newcombi = []
        index_row = 0
        chance = 1

        if chance == 1:
            for row in combi:
                if rate == random.randint(0, totalrate):
                    newrow = self.shuffle(
                        row, self.LOCKED[index_row])  # Shuffle row
                    newcombi.append(newrow)

                else:
                    newcombi.append(row)

                index_row += 1

        # if chance == 2:
        #     for j in range(4):
        #         col = []
        #         for i in range(4):
        #             col.append(combi[i][j])

        #         if rate == random.randint(0, totalrate):
        #             newcol = self.shuffle(row, self.LOCKED[index_row])
        #             newcombi.append(newrow)
        #         index_row += 1

        return newcombi

    def start(self, selection_m="rank"):
        '''
        Starts the genetic algorithm, is the main function
        '''
        # Act as a buffer before starting
        # inpt = input("Press enter here to start")

        population = self.create_starting_population(
            self.POPULATION_SIZE)  # Create random, starting population

        # Starting fitness scores and combinations to get replaced by better ones
        elite_points = [10000, 10000, 1000]
        elites = [[], [], []]

        for i in range(100001):  # Starts the algorithm
            self.y.append(i)
            found = False  # Flag for ig solution found
            # Goes through pruning / selection process

            if selection_m == "rank":
                ranks = self.rank_population(
                    population)  # Ranks each combination
                selected = self.selection(
                    population, ranks, self.SURVIVAL_SIZE)

            else:
                selected = self.tournament_selection_gpt(
                    population, self.SURVIVAL_SIZE)

            # Picks three best as elites from the selected
            new_elites = selected[-3:]

            count = 0
            newelitepoints = []
            # Compares current elites with global elites from previous generations. If better, replace old elite with new elite
            for new_elite in new_elites:
                # Get fitness score of current elite
                new_elite_point = self.find_fitness(new_elite)
                newelitepoints.append(new_elite_point)

                # If smaller (better), then replace
                if new_elite_point < elite_points[count]:
                    if new_elite in elites:
                        pass
                    else:
                        elites[count] = new_elite
                        elite_points[count] = new_elite_point

                count += 1

            self.ALLSCORES.append(min(newelitepoints))
            self.ALLELITESCORES.append(min(elite_points))

            # Update current best score in window
            self.score.config(text=min(elite_points))
            # Update current generation in window
            self.generation.config(text=i)

            population = []

            points_count = 0

            # Updates the sudoku with the solution if found
            for points in elite_points:
                if points == 0:
                    tkinter_row = 0
                    tkinter_digit = 0
                    for row in elites[points_count]:
                        for digit in row:
                            self.cells[tkinter_row][tkinter_digit].config(
                                text=digit)

                            tkinter_digit += 1

                        tkinter_row += 1
                        tkinter_digit = 0
                        print(row)
                    found = True

                    return self.y, self.ALLELITESCORES, self.ALLSCORES
                    # break
                points_count += 1

            if found:
                break  # Stops program if found

            # Adds the 3 global elites to new population, updates sudoku with each elite combination
            for item in elites:
                tkinter_row = 0
                tkinter_digit = 0
                if item != []:
                    for row in item:
                        for digit in row:
                            self.cells[tkinter_row][tkinter_digit].config(
                                text=digit)
                            tkinter_digit += 1

                        tkinter_row += 1
                        tkinter_digit = 0

                    population.append(item)

            for combinaiton in selected:
                index = 0
                for j in range(len(selected)):
                    if index == j:  # If index is same as the current combination, do not crossover
                        pass

                    # Chance to either crossover or add old combination to new population (chance still editing)
                    if random.randint(1, 1) == 1:
                        offspring = self.crossover(combinaiton, selected[j])
                        child1 = self.mutation(offspring[0], 1, 1000)
                        child2 = self.mutation(offspring[1], 1, 1000)

                        if child1 not in population:
                            population.append(child1)

                        if child2 not in population:
                            population.append(child2)

                    if random.randint(1, 5) == 1:
                        if combinaiton not in population:
                            population.append(combinaiton)

                index += 1


root = tk.Tk()
app = App(root)
board = app.BOARD

root.mainloop()

root2 = tk.Tk()
app2 = App(root2, board=board)

root2.mainloop()

plt.plot(app.y, app.ALLSCORES,
         label="Local Best score from generation")
plt.plot(app.y, app.ALLELITESCORES,
         label="Global best score from generation")

plt.plot(app2.y, app2.ALLSCORES,
         label="Local Best score from generation (RANK)")
plt.plot(app2.y, app2.ALLELITESCORES,
         label="Global best score from generation (RANK)")

plt.ylabel('Points')
plt.xlabel('generation')

plt.legend()
plt.show()
