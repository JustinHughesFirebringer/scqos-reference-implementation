import sys, numpy as np
from scipy.integrate import quad
from scipy.stats import chi2, norm
D=sys.argv[1]
rows=[l.split() for l in open(D+"/desi_gaussian_bao_ALL_GCcomb_mean.txt") if l.strip() and not l.startswith("#")]
z=np.array([float(r[0]) for r in rows]); y=np.array([float(r[1]) for r in rows]); k=[r[2] for r in rows]
C=np.loadtxt(D+"/desi_gaussian_bao_ALL_GCcomb_cov.txt"); c=299792.458
def model(H0,Om,rd,Or=0.0):
    E=lambda x: np.sqrt(Om*(1+x)**3+Or*(1+x)**4+1-Om-Or)
    out=[]
    for zi,ki in zip(z,k):
        DH=c/(H0*E(zi)); DM=c/H0*quad(lambda x:1/E(x),0,zi)[0]
        out.append({"DM_over_rs":DM,"DH_over_rs":DH,"DV_over_rs":(zi*DM*DM*DH)**(1/3)}[ki]/rd)
    return np.array(out)
def chi(m): d=y-m; return float(d@np.linalg.solve(C,d))
h=0.674; Or=2.47e-5*(1+0.2271*3.046)/h**2
for lab,m in [("as published (rounded Planck, no radiation)",model(67.4,0.315,147.09)),
              ("+ radiation",model(67.4,0.315,147.09,Or)),
              ("Planck 2018 exact best-fit H0=67.36 Om=0.3153",model(67.36,0.3153,147.09,Or))]:
    x=chi(m); p=chi2.sf(x,13); print(f"{lab:48s} chi2={x:6.2f}  p={p:.4f}  (~{norm.isf(p/2):.1f} sigma)")
