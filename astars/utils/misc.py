# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 10:20:16 2020

@author: varis
"""


import numpy as np
def subspace_dist(obasis,obasis2):
    if obasis.ndim == 1:
        obasis=obasis.reshape(-1,1)
    if obasis2.ndim == 1:
        obasis2=obasis2.reshape(-1,1)
    d=np.maximum(obasis.shape[1],obasis2.shape[1])
    ans = d-np.sum(obasis.T@obasis2)**2
    ans = np.maximum(0.0,ans)
    return np.sqrt(ans)
    

def find_active(eigval,eigvec,threshold = .95, verbose = False, dimensions = None):
    
    
    
    target = threshold * np.sum(eigval)
    svar=0
    adim=0
    dim=np.size(eigval)
    while svar < target and adim<dim:
        svar += eigval[adim]
        adim+=1
    print ('Subspace Dimension', adim)
    if verbose: 
        print(eigval[0:adim])
        print('Subspace',eigvec[:,0:adim])

    return adim 
    
