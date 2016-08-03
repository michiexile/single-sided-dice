# Simulator scaffold for single sided dice question

@futurebird on Twitter writes:

    Strange dice! Set of 6, each has 1 number. Can you think of a way to use all 6 together like a normal die?
    To clarify the challenge is to roll all 6 together and *easily* produce the same probability distribution of a 6-sided die?
    
With this package you can test possible solution attempts.

Write a function in Python that responds with either a dice value, or a list of dice to reroll. 
The simulator keeps rerolling as requested up to a parametrized reroll count, and then collects
the results.

Your function should take a list of objects, and return either a list of integers, or a single integer.
The objects handed to the function are named tuples with fields:

* `position`, a pair of integers uniformly drawn from `[0,200]x[0,200]`
* `value`, single integer in `[0,6]`. The value is 0 if the value field is facing the table *and* 
   the option `hidden-visible` is set.
* `direction`, either one of `'up'`, `'down'`, `'side'`, `'north'`, `'east'`, `'south'`, `'west'` or an integer
  in `[0,359]`.
  
The simulator takes options controlling the input to the model. The parameter `options` should be a `dict`
with some of these keys set:

* `'position'`: boolean. If `True`, the position field is included for the function
* `'values'`: string, one of `'up-other'`, `'up-side-down'`, `'up-4-down'`, `'up-360-down'`, controlling
  what values are assigned to the `direction` field
* `'hidden-visible'`, uses the 0 value for the `value` field

The simulator does a chi-squared test for fit to the uniform distribution, and returns the chi-squared coefficient
as well as the probability of a chi-squared variable being at most the computed value, providing a measure
of goodness of fit for the simulated approach.

As an example, the code includes the possible solution of rerolling all non-blank results until only one
result is non-blank, and if so use that result as the response.

```
    def decision(ss):
        full = [j for j in range(6) if ss[j].direction != 'down']
        if len(full) != 1:
            return [j for j in range(6) if j in full]
        return full[0]
```

running this, produces (for instance) the results
```
    converged trials: 47.5% 475
    histogram
	  [0.16631578947368422, 0.17473684210526316, 0.1705263157894737, 0.15789473684210525, 0.15368421052631578, 0.17684210526315788]
    chi2: 0.002575069252077564    cdf: 1.7882230765945254e-08
```

