__author__ = 'jheaton'

import numpy as np
import sys


class Train(object):
    def __init__(self, goal_minimize=True):
        self.max_iterations = 100000
        self.position = []
        self.best_score = 0
        self.goal_minimize = goal_minimize
        self.display_final = True
        self.display_iteration = False
        self.stop_score = None

    def better_than(self, is_this, than_that):
        if self.goal_minimize:
            return is_this < than_that
        else:
            return is_this > than_that

    def should_stop(self, iteration, best_score):
        if iteration > self.max_iterations:
            return True

        if self.stop_score is not None:
            if self.better_than(best_score, self.stop_score):
                return True

        return False


class TrainGreedRandom(Train):
    def __init__(self, low, high, goal_minimize=True):
        self.high = low
        self.low = high
        Train.__init__(self, goal_minimize)

    def train(self, x0, funct):
        iteration_number = 1
        self.position = x0[:]
        self.best_score = funct(self.position)

        while self.should_stop(iteration_number, self.best_score) == False:
            # Clone current position, create a new array of same size.
            trial_position = self.position[:]
            # Randomize trial position.
            self.perform_randomization(trial_position)
            # Obtain new trial score.
            trial_score = funct(trial_position)

            if self.better_than(trial_score, self.best_score):
                self.best_score = trial_score
                self.position = trial_position

            current = funct(self.position)

            if self.display_iteration:
                print("Iteration #" + str(iteration_number) + ", Score: " + str(self.best_score))
            iteration_number += 1

        if self.display_final:
            print("Finished after " + str(iteration_number) + " iterations, final score is " + str(self.best_score))

    def perform_randomization(self, vec):
        for i in xrange(0, len(vec)):
            vec[i] = np.random.uniform(self.low, self.high)


class TrainHillClimb(Train):
    def __init__(self, goal_minimize=True):
        Train.__init__(self, goal_minimize)

    def train(self, x0, funct, acceleration=1.2, step_size=1.0):
        iteration_number = 1
        self.position = x0[:]
        self.best_score = funct(self.position)

        step_size = [step_size] * len(x0)

        candidate = [0] * 5
        candidate[0] = -acceleration
        candidate[1] = -1 / acceleration
        candidate[2] = 0
        candidate[3] = 1 / acceleration
        candidate[4] = acceleration

        while self.should_stop(iteration_number, self.best_score) == False:
            # Clone current position, create a new array of same size.
            trial_position = self.position[:]

            if self.goal_minimize:
                best_step_score = sys.float_info.max
            else:
                best_step_score = sys.float_info.min

            for dimension in xrange(0, len(self.position)):
                best = -1
                for i in xrange(0, len(candidate)):
                    # Take a step
                    trial_position[dimension] += candidate[i] * step_size[dimension]
                    # Obtain new trial score.
                    trial_score = funct(trial_position)
                    # Step back, we only want to try movement in one dimension.
                    trial_position[dimension] -= candidate[i] * step_size[dimension]

                    # Record best step taken
                    if self.better_than(trial_score, best_step_score):
                        best_step_score = trial_score
                        best = i

                if best <> -1:
                    self.best_score = best_step_score
                    trial_position[dimension] += candidate[best] * step_size[dimension]
                    step_size[dimension] = step_size[dimension] * candidate[best];

            if self.display_iteration:
                print("Iteration #" + str(iteration_number) + ", Score: " + str(self.best_score))
            iteration_number += 1

        if self.display_final:
            print("Finished after " + str(iteration_number) + " iterations, final score is " + str(self.best_score))


class TrainAnneal(Train):
    def __init__(self, max_iterations = 1000, start_temperature=400, ending_temperature = 0.0001):
        Train.__init__(self, True)
        self.max_iterations = max_iterations
        self.start_temperature = start_temperature
        self.ending_temperature = ending_temperature
        self.cycles = 100

    def train(self, x0, funct):
        iteration_number = 1
        self.position = x0[:]
        self.best_score = funct(self.position)

        while self.should_stop(iteration_number, self.best_score) == False:
            # Clone current position, create a new array of same size.
            trial_position = self.position[:]
            # Randomize trial position.
            self.perform_randomization(trial_position)
            # Obtain new trial score.
            trial_score = funct(trial_position)

            keep = False
            current_temperature = self.cooling_schedule(current_temperature)

            if self.better_than(trial_score, self.best_score):
                keep = True
            else:
                self.last_probability = self.calc_probability(self.best_score,trial_score,current_temperature)
                if self.last_probability > np.random.uniform() :
                    self.best_score = trial_score
                    self.position = trial_position

            if self.display_iteration:
                print("Iteration #" + str(iteration_number) + ", Score: " + str(self.best_score))
            iteration_number += 1

        if self.display_final:
            print("Finished after " + str(iteration_number) + " iterations, final score is " + str(self.best_score))

    def perform_randomization(self, vec):
        for i in xrange(0, len(vec)):
            vec[i] = np.random.uniform(self.low, self.high)

    def calc_probability(self, error_current, error_new, t):
        return np.exp(-(np.abs(error_new - error_current) / t))

    def cooling_schedule(self, current_iteration):
        ex = float(current_iteration) / float(self.max_iterations)
        return self.startingTemperature * (self.endingTemperature / self.startingTemperature) ** ex

    def perform_randomization(self, vec):
        for i in xrange(0, len(vec)):
            d = np.random.normal() * 3