#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 15:06:33 2020

@author: cmg
"""

import numpy as np
import matplotlib.pyplot as plt
import timeit
import active_subspaces as ss   
from astars.stars_sim import Stars_sim
from astars.utils.misc import subspace_dist, find_active
import pandas as pd

###############################################################################
############ Set user-desired file path for storing output data!!! ############
###############################################################################
user_file_path = '/home/ccm/Desktop/'
###############################################################################
###############################################################################
###############################################################################

class toy2:
        def __init__(self, mag = 1.0, dim = 20, weights = None, sig = 1E-6):
                self.mag = mag
                self.dim = dim
                self.L1 = self.mag*self.dim*2.0
                self.sig = sig
                self.var = self.sig**2
                self.name = 'Example 1: STARS, FAASTARS, and ASTARS Convergence'
                self.nickname = 'toy_2'
                self.fstar = 0
                if weights is None:
                    self.weights = np.ones(self.dim)
                self.active = self.weights / np.linalg.norm(self.weights)
                self.active = self.active.reshape(-1,1)
                
                self.maxit = 2*dim**2
                self.ntrials = 100
                self.adapt = 2*dim
                self.regul = None
                self.threshold = 0.99
                self.initscl = 10.0
            
   
        def __call__(self, x):
            return self.mag*(np.dot(self.weights,x)**2) + self.sig*np.random.randn(1)

class toy_sqr:
        def __init__(self, mag = 1.0, dim = 20, weights = None, sig = 1E-6):
                self.mag = mag
                self.dim = dim
                self.L1 = self.mag*self.dim*12.0
                self.sig = sig
                self.var = self.sig**2
                self.name = 'Example 1: STARS, FAASTARS, and ASTARS Convergence'
                self.nickname = 'toy_2'
                self.fstar = 0
                if weights is None:
                    self.weights = np.ones(self.dim)
                self.active = self.weights / np.linalg.norm(self.weights)
                self.active = self.active.reshape(-1,1)
                
                self.maxit = 2*dim**2
                self.ntrials = 5
                self.adapt = 2*dim
                self.regul = None
                self.threshold = 0.99
                self.initscl = 1.0
            
   
        def __call__(self, x):
            return self.mag*(np.dot(self.weights,x)**4) + self.sig*np.random.randn(1)
            
#sphere function, was toy 1
           
class sphere:
        def  __init__(self, mag = 1.0, dim = 20, adim = 10, sig = 1E-3):
              self.dim = dim
              self.adim = adim
              self.sig = sig
              self.mag = mag
              self.active = np.eye(dim,adim)
              self.L1 = 2.0*self.mag
              self.var = self.sig**2
              self.name = 'Example 2: STARS, FAASTARS, and ASTARS Convergence'
              self.nickname = 'sphere'
              self.fstar = 0
              
              self.maxit = 2*dim**2
              self.ntrials = 10
              self.adapt = dim
              self.regul = self.sig**2
              self.threshold = 0.999
              self.initscl = 10.0
            
        def __call__(self,X):
            return self.mag*np.sum(X[0:self.adim]**2) + self.sig*np.random.randn(1)
 
class nesterov_2_f:
    
    def __init__(self, dim = 50, adim = 5, sig = 1E-4):
        self.dim = dim
        self.adim = adim
        self.sig = sig
        self.active = np.eye(dim,adim)
        self.L1 = 4.0
        self.var = self.sig**2
        self.name = 'Example 3: STARS, FAASTARS, and ASTARS Convergence'
        self.nickname = 'nesterov_2'
        self.fstar = .5*(-1 + 1 / (self.adim + 1))
        self.maxit = 6000
        self.ntrials = 10 #50
        self.adapt = 2*dim
        self.regul = self.sig**2
        self.threshold = .9 # ideal for this setup: 0.999
        self.initscl = 50.0
    
    def __call__(self,x):
        
        ans = 0.5*(x[0]**2 + x[self.adim-1]**2) - x[0]
        for i in range(self.adim-1):
            ans += .5*(x[i] - x[i+1])**2
            if ans.ndim == 1:
                ans += self.sig*np.random.randn(1)
            else:
                ans += self.sig*np.random.randn(ans.size)
        return ans
    


#plotting parameters and definitions
toy2f = toy_sqr()
sph = sphere()
nest = nesterov_2_f()


params = {'legend.fontsize': 28,'legend.handlelength': 3}
plt.rcParams["figure.figsize"] = (60,40)
plt.rcParams['figure.dpi'] = 80
plt.rcParams['savefig.dpi'] = 100
plt.rcParams['font.size'] = 30
plt.rcParams['figure.titlesize'] = 'xx-large'
plt.rcParams.update(params)

stars_full, sf_ls = 'red', '--'
active_stars_learned, lr_ls = 'black', '-.'
active_stars_ref, rf_ls = 'blue', ':'


# Start the clock!
start = timeit.default_timer()


for f in {toy2f, sph, nest}:
    dim = f.dim
    np.random.seed(9)
    init_pt = f.initscl*np.random.randn(dim)
    ntrials = f.ntrials
    maxit = f.maxit

    f3_avr = np.zeros(maxit+1)
    f2_avr = np.zeros(maxit+1)
    f_avr = np.zeros(maxit+1)
    
  
    

    
    # STARS
    for trial in range(ntrials):
    #sim setup
        test = Stars_sim(f, init_pt, L1 = f.L1, var = f.var, verbose = False, maxit = maxit)
        test.STARS_only = True
        test.get_mu_star()
        test.get_h()
    # do 100 steps
        while test.iter < test.maxit:
            test.step()
    
    #update average of f
        f_avr += test.fhist
        

        print('STARS trial',trial,' minval',test.fhist[-1])

    # FAASTARS
    for trial in range(ntrials):
        #sim setup
        test = Stars_sim(f, init_pt, L1 = f.L1, var = f.var, verbose = False, maxit = maxit, true_as = f.active)
        test.get_mu_star()
        test.get_h()
        # adapt every f.adapt timesteps using quadratic(after inital burn)
        test.train_method = 'GQ'

        test.adapt = f.adapt # Sets retraining steps
        #test.subcycle = True # turn on subcycling
        test.threshadapt = True

        #test.debug = True
        test.regul = f.regul
        test.threshold = f.threshold
        
        # do 100 steps
        while test.iter < test.maxit:
            test.step()
            if test.active is not None and test.iter // test.adapt:
               print('distance',subspace_dist(test.active,f.active))

        f2_avr += test.fhist
        


        print('FAASTARS trial',trial,' minval',test.fhist[-1])
    
    # ASTARS
    for trial in range(ntrials):
        
        test = Stars_sim(f, init_pt, L1 = f.L1, var = f.var, verbose = False, maxit = maxit)
        test.active = f.active
        test.get_mu_star()
        test.get_h()
        test.adapt = 0
    # do 100 steps
        while test.iter < test.maxit:
            test.step()
    
    #update average of f
        f3_avr += test.fhist  

        print('True ASTARS trial',trial,' minval',test.fhist[-1])
        
    f_avr /= ntrials
    f2_avr /= ntrials
    f3_avr /= ntrials
    

  

        
    # Stop the clock!
    stop = timeit.default_timer()

    # Difference stop-start tells us run time
    time = stop - start
    print('the time of this experiment was:    ', time/3600, 'hours')
 
    plt.semilogy(np.abs(f_avr-f.fstar),lw = 5,label='STARS',color=stars_full, ls=sf_ls)
    plt.semilogy(np.abs(f2_avr-f.fstar), lw = 5, label='FAASTARS (Approx $\\tilde{\mathcal{A}}$)',color=active_stars_learned ,ls=lr_ls)
    plt.semilogy(np.abs(f3_avr-f.fstar), lw = 5,label = 'ASTARS (True $\mathcal{A}$)',color=active_stars_ref ,ls=rf_ls)
    plt.title(f.name)
    plt.xlabel('$k$, iteration count')
    plt.ylabel('$|f(\lambda^{(k)})-f^*|$')
    plt.legend()
    plt.show()

