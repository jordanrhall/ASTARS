#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 9/1/2020

@author: jordan/varis
"""

import numpy as np
import matplotlib.pyplot as plt

import active_subspaces as ss   
from astars.stars_sim import Stars_sim
from astars.utils.misc import subspace_dist, find_active

class nesterov:
    
    def __init__(self, dim = 10, sig = 1E-4):
        self.dim = dim
        self.sig = sig
        self.L1 = 2**11
        self.var = self.sig**2
        self.name = 'Nesterov'
        self.fstar = 0
    
    def __call__(self,x):
        
        temp = np.arange(self.dim,dtype=float)
        weights = 2**((-1)**temp*temp)
        y = np.copy(x)
        y *= y
        ans = np.dot(weights,y) +self.sig*np.random.randn(1)

        return ans
        
f = nesterov()

thresholds = [0.9,0.99,0.999,0.9999]
this_init_pt = np.random.randn(f.dim)

ntrials = 10
maxit = 20000

f_avr = np.zeros(maxit+1)
f2_avr = np.zeros((maxit+1,np.size(thresholds)))
print(np.size(thresholds))

# STARS
for trial in range(ntrials):
    test = Stars_sim(f, this_init_pt, L1 = f.L1, var = f.var, verbose = False, maxit = maxit)
    test.STARS_only = True
    test.get_mu_star()
    test.get_h()
    # do stars steps
    while test.iter < test.maxit:
        test.step()
	    
    #update average of f
    f_avr += test.fhist
    print('STARS trial',trial,' minval',test.fhist[-1])

for i in range(np.size(thresholds)):
        
    for trial in range(ntrials):
        test = Stars_sim(f, this_init_pt, L1 = f.L1, var = f.var, verbose = False, maxit = maxit)
        test.get_mu_star()
        test.get_h()
        test.train_method = 'GQ'
        test.adapt = 3.0*f.dim # Sets number of sub-cylcing steps
        test.regul = None #test.sigma
        test.threshold = thresholds[i]
	# do 100 steps
        while test.iter < test.maxit:
            test.step()  

        f2_avr[:,i] += test.fhist
        print('ASTARS trial',trial,' minval',test.fhist[-1])
	    
f_avr /= ntrials
f2_avr /= ntrials

print(f_avr)
print(f2_avr)
plt.semilogy(np.abs(f_avr-f.fstar),label='STARS')
for i in range(np.size(thresholds)):
    plt.semilogy(np.abs(f2_avr[:,i]-f.fstar), label='ASTARS, thresh='+str(thresholds[i]))

plt.title(f.name)
plt.legend()
plt.show()
