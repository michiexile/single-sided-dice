# -*- coding: utf-8 -*-
__author__ = 'mik'

"""
Library file (not executable) with a simulator for the one-marked dice
 problem. Use the function `simulate` to run a simulation, hand it
 a function `model` to control rerolls and predictions.

simulate(
  model      : simulator_structure -> int or list
  options    : dict, see type below
  n          : int, number of trials
  maxrerolls : int, number of rerolls until giving up
  ) -> return structure

simulator structure is a list or set, each element a named tuple that may have the
following fields:
  'position'  : (float, float)
  'value'     : int in [0..6]; 0 means not visible / not available
  'direction' : one of 'up', 'down', 'side', 'north', 'south', 'east', 'west', float

type is a dict, which may have the following fields; given with
the assumed default value if missing listed first:
  'position'       : True
  'values'         : 'up-other', 'up-side-down', 'up-4-down', 'up-360-down'
  'hidden-visible' : False, return list, distinguishing dice even if value not visible

return structure is a dict, with some subset of the following fields:
  'rolls'       : list of simulator structures
  'predictions' : list of model returned values
  'histogram'   : percentages of each outcome
  'chi2'        : chi2 estimator to test equivalence to a uniform distribution
  'cdf'         : cdf(chi2); p-value

chi2 setup following John Cook http://www.johndcook.com/blog/2016/06/08/prime-remainders-too-evenly-distributed/
"""

import random
import collections
import scipy.stats

def roll(angle=False):
    result = random.choice(['up', 'down', 'north', 'east', 'south', 'west'])
    if angle and result in ['north', 'east', 'south', 'west']:
        result = random.randint(0,359)
    return result

ModelInput = collections.namedtuple('ModelInput', ['position', 'value', 'direction'])
def simulate(model=lambda structure: 1, options=dict(), maxrerolls=100, n=1000):
    if 'position' in options:
        position = options['position']
    else:
        position = True

    if 'values' in options:
        values = options['values']
    else:
        values = 'up-other'
    angle = values == 'up-360-down'

    if 'hidden-visible' in options:
        hidden_visible = options['hidden-visible']
    else:
        hidden_visible = False


    return_dict = {'rolls': [], 'predictions': []}
    # core loop for the simulation
    for _ in range(n):
        value = range(6)
        diceroll = [None]*6
        for _ in range(maxrerolls):
            for i in value:
                diceroll[i] = roll(angle=angle)
            modelinput = [{'direction': diceroll[i], 'position': (random.randint(0,200), random.randint(0,200))}
                          for i in range(6)]
            if not position:
                modelinput['position'] = None
            if values == 'up-other':
                for i in range(6):
                    if modelinput[i]['direction'] != 'up':
                        modelinput[i]['direction'] = 'down'
            if values == 'up-4-down':
                for i in range(6):
                    if modelinput[i]['direction'] not in ['up', 'down']:
                        modelinput[i]['direction'] = 'side'
            for i in range(6):
                modelinput[i]['value'] = i+1
                modelinput[i] = ModelInput(**modelinput[i])
            if hidden_visible:
                for i in range(6):
                    if modelinput[i]['direction'] == 'down':
                        modelinput[i]['value'] = 0
                modelinput = set(modelinput)
            value = model(modelinput)
            if type(value) is not list:
                return_dict['rolls'].append(diceroll)
                return_dict['predictions'].append(value+1)
                break



    result = collections.Counter(return_dict['predictions'])
    percentages = [result[i]/len(return_dict['predictions']) for i in range(1,7)]
    chi2 = sum([(result[i]/len(return_dict['predictions']) - 1/6)**2/(1/6) for i in range(1,7)])
    return_dict['chi2'] = chi2
    return_dict['cdf'] = scipy.stats.chi2.cdf(chi2, df=6-1)
    return_dict['histogram'] = percentages
    return return_dict

def decision(ss):
    full = [j for j in range(6) if ss[j].direction != 'down']
    if len(full) != 1:
        return [j for j in range(6) if j in full]
    return full[0]


if __name__ == '__main__':
    result = simulate(model=decision)
    print('converged trials: {}% {}'.format(100*len(result['predictions'])/1000, len(result['predictions'])))
    print('histogram\n\t{}'.format(result['histogram']))
    print('chi2: {}\tcdf: {}'.format(result['chi2'], result['cdf']))
