#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 15:06:33 2020

@author: cmg
"""

import numpy as np
import matplotlib.pyplot as plt

import active_subspaces as ss   
from astars.stars_sim import Stars_sim
from astars.utils.misc import subspace_dist, find_active

class toy2:
        def __init__(self, mag = 1.0, dim = 20, weights = None, sig = 1E-6):
                self.mag = mag
                self.dim = dim
                self.L1 = self.mag*self.dim*2.0
                self.sig = sig
                self.var = self.sig**2
                self.name = 'Toy 2'
                if weights is None:
                    self.weights = np.ones(self.dim)
 
   
        def __call__(self, x):
            return self.mag*(np.dot(self.weights,x)**2) + self.sig*np.random.randn(1)


            
#sphere function, was toy 1
           
class sphere:
        def  __init__(self, mag = 1.0, dim = 20, adim = 1, sig = 1E-3):
              self.dim = dim
              self.adim = adim
              self.sig = sig
              self.mag = mag
        
              self.L1 = 2.0*self.mag
              self.var = self.sig**2
              self.name = 'Active Sphere'
            
        def __call__(self,X):
            return np.sum(X[0:self.adim]**2) + self.sig*np.random.randn(1)
    
#def toy_f(x,var=1E-6):
#    return mag*(np.dot(weights,x))**2 + var*np.random.randn(1)
#true_as = weights / np.linalg.norm(weights)
#toy_l1 = mag*dim*2.0




toy2f = toy2()
sph = sphere()

for f in {toy2f,sph}:
    dim = f.dim
    init_pt = 10*np.random.rand(dim)
    ntrials = 5
    #maxit = dim**2
    maxit = 1000
    f2_avr = np.zeros(maxit+1)
    f_avr = np.zeros(maxit+1)
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
 
    for trial in range(ntrials):
        #sim setup
        test = Stars_sim(f, init_pt, L1 = f.L1, var = f.var, verbose = False, maxit = maxit)
        test.get_mu_star()
        test.get_h()
        # adapt every 10 timesteps using quadratic(after inital burn)
        test.train_method = 'GQ'
        test.adapt = dim # Sets number of sub-cylcing steps
        #test.regul *= 100
        #test.debug = True
        test.regul = None
        # do 100 steps
        while test.iter < test.maxit:
            test.step()  
            #if test.iter % 20 == 0 and test.active is not None:
            #    print('Step',test.iter,'Active dimension',test.active.shape[1])
            #    print('Subspace Distance',subspace_dist(true_as,test.active))
            # Normalization test
            #sub_sp = ss.subspaces.Subspaces()
            #train_x=np.hstack((test.xhist[:,0:test.iter+1],test.yhist[:,0:test.iter]))
            #train_f=np.hstack((test.fhist[0:test.iter+1],test.ghist[0:test.iter]))
            #sub_sp.compute(X=train_x.T,f=train_f,sstype='QPHD')
            #usual threshold
            #adim = find_active(sub_sp.eigenvals,sub_sp.eigenvecs)
            #print('Subspace Distance, no scaling, raw call',subspace_dist(true_as,sub_sp.eigenvecs[:,0:adim]))
        f2_avr += test.fhist
        print('ASTARS trial',trial,' minval',test.fhist[-1])
    
    
    

    f_avr /= ntrials
    f2_avr /= ntrials
 
    plt.semilogy(f_avr,label='Stars')
    plt.semilogy(f2_avr, label='Astars')
    plt.title(f.name)
    plt.legend()
    plt.show()

def get_mat(X,f):
    #un-normalized computation
    gquad = ss.utils.response_surfaces.PolynomialApproximation(N=2)
    gquad.train(X, f, regul =None) #regul = self.var)
    # get regression coefficients
    b, A = gquad.g, gquad.H
    C = np.outer(b, b.transpose()) + 1.0/3.0*np.dot(A, A.transpose())
    sub_sp.eigenvals,sub_sp.eigenvecs = ss.subspaces.sorted_eigh(C)
    adim = find_active(sub_sp.eigenvals,sub_sp.eigenvecs)
    print('Subspace Distance, direct call with regul',subspace_dist(true_as,sub_sp.eigenvecs[:,0:adim]))
    #print(gquad.H[0,0])
    print('Active subspace, first vector',sub_sp.eigenvecs[:,0])
    
    #mapped math
    lb = np.amin(X,axis=0).reshape(-1,1)
    ub = np.amax(X,axis=0).reshape(-1,1)
    #print(lb.shape)
    nrm_data=ss.utils.misc.BoundedNormalizer(lb,ub)

    #print(lb,ub)
    xhat=nrm_data.normalize(X)
    
    scale = .5*(ub-lb)
    print('scaling vector', scale)
    gquad.train(xhat,f, regul = None)
    b2, A2 = gquad.g, gquad.H
    C2 = np.outer(b2,b2.transpose()) + 1.0/3.0*np.dot(A2,A2.transpose())
    D = np.diag(1.0/scale.flatten())
    #print(D)
    C2 = D @ C2 @ D
    
    sub_sp.eigenvals,sub_sp.eigenvecs = ss.subspaces.sorted_eigh(C2)
    adim = find_active(sub_sp.eigenvals,sub_sp.eigenvecs)
    print('Subspace Distance, after mapping',subspace_dist(true_as,sub_sp.eigenvecs[:,0:adim]))
    #print(gquad.H[0,0])
    print('Active subspace, first vector',sub_sp.eigenvecs[:,0])
    
#get_mat(train_x.T,train_f)