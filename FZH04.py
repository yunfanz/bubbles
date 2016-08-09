import numpy as n, matplotlib.pyplot as p, scipy.special
import cosmolopy.perturbation as pb
import cosmolopy.density as cd
from scipy.integrate import quad,tplquad
import itertools
from scipy.interpolate import interp1d
from scipy.interpolate import RectBivariateSpline as RBS
import optparse, sys

o = optparse.OptionParser()
o.add_option('-d','--del0', dest='del0', default=5.)
o.add_option('-m','--mul', dest='mul', default=1.)
o.add_option('-z','--red', dest='red', default=12.)
opts,args = o.parse_args(sys.argv[1:])
print opts, args

Om,sig8,ns,h,Ob = 0.315, 0.829, 0.96, 0.673, 0.0487
Planck13 = {'baryonic_effects':True,'omega_k_0':0,'omega_M_0':0.315, 'omega_b_0':0.0487, 'n':0.96, 'N_nu':0, 'omega_lambda_0':0.685,'omega_n_0':0., 'sigma_8':0.829,'h':0.673}
cosmo = Planck13
def m2R(m):
	rhobar = cd.cosmo_densities(**cosmo)[1]  #msun/Mpc
	RL = (3*m/4/n.pi/rhobar)**(1./3)
	return RL
def m2V(m):
	rhobar = cd.cosmo_densities(**cosmo)[1]  #msun/Mpc
	return m/rhobar

def R2m(RL):
	rhobar = cd.cosmo_densities(**cosmo)[1]  #msun/Mpc
	m = 4*n.pi/3*rhobar*RL**3
	return m

dmS = n.load('m2S.npz')
MLtemp,SLtemp = dmS['arr_0'],dmS['arr_1']
fs2m = interp1d(SLtemp,MLtemp,kind='cubic')
def S2M(S):
	return fs2m(S)

def mmin(z,Tvir=1.E4):
	return pb.virial_mass(Tvir,z,**cosmo)
def RG(RL): return 0.46*RL
def W(y): return 3/y**3*(n.sin(y)-y*n.cos(y))
def WG(y): return n.exp(-y**2/2)
def Del2k(k):
	Pk = pb.power_spectrum(k,0.,**cosmo)
	Del2k = k**3*Pk/2/n.pi**2
	#fgrowth = pb.fgrowth(z, cosmo['omega_M_0']) 
	#Del2k0 = Del2k/fgrowth**2#*pb.norm_power(**cosmo)
	return Del2k
#def sig0(RL,Del2k):
#	return n.sum(Del2k**2*W(RL*k)**2)*(logk[1]-logk[0])
#def sig0(RL,Del2k):
#	return n.sum(Del2k**2*W(RL*k)**2/k)*(k[1]-k[0])
def polyval2d(x, y, m):
    order = int(n.sqrt(len(m))) - 1
    ij = itertools.product(range(order+1), range(order+1))
    z = n.zeros_like(x)
    for a, (i,j) in zip(m, ij):
        z += a * x**i * y**j
    return z
#def sig0test(RL,kmax):
#	return quad(lambda k: Del2k(k)*W(RL*k)**2/k, 0, kmax)[0]   #z=0 extrapolated to present
#def sig0(RL):
#	return (pb.sigma_r(RL,0.,**cosmo)[0])**2
#def sigG(RL,j): 
#	return (pb.sigma_j(RL,j,0.,**cosmo)[0])**2
# dsig1m = n.load('sig1m.npz')
# sig1mRl,sig1marr = dsig1m['arr_0'],dsig1m['arr_1']
# fs1m = interp1d(sig1mRl,sig1marr,kind='cubic')
# def sig1m(RL):
# 	return fs1m(RL)
# dSX = n.load('logSX.npz')
# lSXRl,lSXR0,arrSX = dSX['arr_0'],dSX['arr_1'],dSX['arr_2']
# fSX = RBS(lSXRl,lSXR0,arrSX)
# def SX(RL,R0):
# 	res = fSX(n.log(RL),n.log(R0))
# 	if res.size > 1: print 'Warning: SX called with array instead of single number'
# 	return res[0][0]
# ds1mX = n.load('logsig1mX.npz')
# ls1mXRl,ls1mXR0,arrs1mX = ds1mX['arr_0'],ds1mX['arr_1'],ds1mX['arr_2']
# fs1mX = RBS(ls1mXRl,ls1mXR0,arrs1mX)
# def sig1mX(RL,R0):
# 	res = fs1mX(n.log(RL),n.log(R0))
# 	if res.size > 1: print 'Warning: s1mX called with array instead of single number'
# 	return res[0][0]
def ig_sig0(RL,k):
    return Del2k(k)*W(RL*k)**2/k
def ig_sigG(RL,j,k):
    return Del2k(k)*(k**(2*j))*WG(RG(RL)*k)**2/k
def ig_sig1m(RL,k):
    return Del2k(k)*(k**2)*WG(RG(RL)*k)*W(RL*k)/k
def ig_sig1mX(RL,R0,k):
    return Del2k(k)*(k**2)*WG(RG(RL)*k)*W(R0*k)/k
def ig_SX(RL,R0,k):
    return Del2k(k)*W(RL*k)*W(R0*k)/k
def sig0(RL,kf=50.,N=2000):
    kmax = kf/RL
    K = n.exp(n.linspace(n.log(0.0001),n.log(kmax),N))
    Y = ig_sig0(RL,K)
    return n.trapz(Y,K) 
def sigG(RL,j,kf=150.,N=1000):
    kmax = kf/RL
    K = n.linspace(0.001,kmax,N)
    Y = ig_sigG(RL,j,K)
    return n.trapz(Y,K) 
def sig1m(RL,kf=15.,N=1000):
    kmax = kf/RL
    K = n.linspace(0.001,kmax,N)
    Y = ig_sig1m(RL,K)
    return n.trapz(Y,K)
def sig1mX(RL,R0,kf=15.,N=1000):
    kmax = kf/RL
    K = n.linspace(0.001,kmax,N)
    Y = ig_sig1mX(RL,R0,K)
    return n.trapz(Y,K)
def SX(RL,R0,kf=10.,N=1000): 
    kmax = kf/RL
    K = n.exp(n.linspace(n.log(0.001),n.log(kmax),N))
    Y = ig_SX(RL,R0,K)
    return n.trapz(Y,K)

def gam(RL):
	return sig1m(RL)/n.sqrt(sig0(RL)*sigG(RL,2))
def Vstar(RL):
	return (6*n.pi)**1.5*n.sqrt(sigG(RL,1)/sigG(RL,2))**3
def erf(x):
	return scipy.special.erf(x)
def prob(x,av=0.5,var=0.25):
	return 1/n.sqrt(2*n.pi*var)/x*n.exp(-(n.log(x)-av)**2/2/var)
def F(x):
	return (x**3-3*x)/2*(erf(x*n.sqrt(5./2))+erf(x*n.sqrt(5./8)))+n.sqrt(2./5/n.pi)*((31.*x**2/4+8./5)*n.exp(-5.*x**2/8)+(x**2/2-8./5)*n.exp(-5.*x**2/2))
def Deltac(z):
	fgrowth = pb.fgrowth(z, cosmo['omega_M_0'])    # = D(z)/D(0)
	return 1.686/fgrowth
def pG(y,av,var):
	return 1/n.sqrt(2*n.pi*var)*n.exp(-(y-av)**2/2/var)
def B(z,beta,s):
	return Deltac(z)+beta*n.sqrt(s)
def Q(m,M0):
	r,R0 = m2R(m), m2R(M0)
	s,s0 = sig0(r), sig0(R0)
	sx = SX(r,R0)
	return 1-sx**2/s/s0
def epX(m,M0):
	r,R0 = m2R(m), m2R(M0)
	s,s0 = sig0(r), sig0(R0)
	sx = SX(r,R0)
	sg1m = sig1m(r)
	sg1mX = sig1mX(r,R0)
	return s*sg1mX/sx/sg1m

#def trapz(x,y):
#	return (x[-1]*y[-1]-x[0]*y[0]+n.sum(x[1:]*y[:-1]-y[1:]*x[:-1]))/2
def trapz(x,y):
	return n.trapz(y,x=x)

def subgrand_trapz_log(b,del0,s,s0,sx,epx,q,meanmu,varmu,varx,gamm,R0,V,z,err=False):
	# EqA8, log intervaled integration axis
	Bb = B(z,b,s)
	#print 'gamm,epx,q =',gamm,epx,q 
	meanx = gamm*((Bb-del0*sx/s0)*(1-epx)/q/n.sqrt(s)+Bb*epx/n.sqrt(s))
	fact = V/Vstar(R0)*pG(Bb/n.sqrt(s),meanmu, varmu)
	#print b, Bb/n.sqrt(s),meanmu,varmu,pG(Bb/n.sqrt(s),meanmu, varmu)
	#print b
	lxmin,lxmax = n.log(b*gamm), n.log(80.)
	lx = n.linspace(lxmin,lxmax,100)
	x = n.exp(lx)
	y = (x/gamm-b)*F(x)*pG(x,meanx,varx)*x
	factint = trapz(x,y)
	#print y
	#print factint
	#factint = quad(lambda x: (x/gamm-b)*F(x)*pG(x,meanx,varx),b*gamm,100)[0]
	#print fact, factint
	return fact*factint
def subgrand_trapz(b,del0,s,s0,sx,epx,q,meanmu,varmu,varx,gamm,R0,V,z,err=False):
	# EqA8, non-log intervaled integration axis
	Bb = B(z,b,s)
	#print 'gamm,epx,q =',gamm,epx,q 
	meanx = gamm*((Bb-del0*sx/s0)*(1-epx)/q/n.sqrt(s)+Bb*epx/n.sqrt(s))
	fact = V/Vstar(R0)*pG(Bb/n.sqrt(s),meanmu, varmu)
	#print b, Bb/n.sqrt(s),meanmu,varmu,pG(Bb/n.sqrt(s),meanmu, varmu)
	#print b
	x = n.linspace(b*gamm,100.,100)                          #TUNE
	y = (x/gamm-b)*F(x)*pG(x,meanx,varx)
	factint = trapz(x,y)
	#print y
	#print factint
	#factint = quad(lambda x: (x/gamm-b)*F(x)*pG(x,meanx,varx),b*gamm,100)[0]
	#print fact, factint
	return fact*factint
def integrand_trapz(del0,m,M0,R0,z):  #2s*f_ESP
    # of A7, divided by 2s; this IS f_ESP
	s = sig0(m2R(m))
	V,r,dmdr = pb.volume_radius_dmdr(m,**cosmo)
	s,s0,sx = sig0(r), sig0(R0),SX(r,R0)
	gamm = gam(r)
	epx,q = epX(m,M0), Q(m,M0)
	meanmu = del0/n.sqrt(s)*sx/s0
	varmu = Q(m,M0)
	varx = 1-gamm**2-gamm**2*(1-epx)**2*(1-q)/q 
	if varx<0:
		print "varx<0, breaking at varx, gamm, epx, q,m,M0="
		print varx, gamm, epx, q, m, M0

#!! varx can be negative

	b = n.arange(0.00001,3.,0.03)
	y = []
	for bx in b:
		newy = prob(bx)*subgrand_trapz(bx,del0,s,s0,sx,epx,q,meanmu,varmu,varx,gamm,R0,V,z)/2/s
		#print 'b,y'
		#print bx,y[-1]
		if n.isnan(newy): 
			print 'NAN detected, breaking at: '
			print bx,prob(bx),del0,s,s0,sx,epx,q,meanmu,varmu,varx,gamm,R0,V
			break
		else:
			y.append(newy)
	return n.trapz(y,b)
	#return quad(lambda b: prob(b)*subgrand_trapz(b,del0,m,M0,z),0,4.)[0]/2/s
def dsdm(m):
	return n.abs(sig0(m2R(m+1))-sig0(m2R(m-1)))/2
# def fcoll(del0,M0,z):
# 	mm = mmin(z)
# 	R0 = m2R(M0)
# 	return quad(lambda m: integrand_trapz(del0,m,M0,R0,z)*dsdm(m),mm,M0)
# def fcoll_trapz(del0,M0,z):
# 	mm = mmin(z)
# 	R0 = m2R(M0)
# 	mx = n.arange(mm,M0,mm)
# 	y = []
# 	for m in mx:
# 		y.append(integrand_trapz(del0,m,M0,R0,z)*dsdm(m))
# 		print m, y[-1]
# 	return n.trapz(y,mx,dx=mm)
# 	#eturn trapz(mx,y)
def fcoll_trapz_log(del0,M0,z,debug=False):
	# Eq. (6)
	print del0
	mm = mmin(z)
	R0 = m2R(M0)
	lmx = n.linspace(n.log(mm),n.log(M0),100)
	y = []
	for lm in lmx:
		m = n.exp(lm)
		y.append(integrand_trapz(del0,m,M0,R0,z)*dsdm(m)*m) #dsdm*m=ds/dln(m)
		#print m, y[-1]
	if debug: 
		return trapz(lmx,y),n.exp(lmx),y
	else:
		return trapz(lmx,y)
def m2S(m):
	return sig0(m2R(m))
######################## SIZE DISTRIBUTION #############################
	####################### FZH04 ##############################

def fFZH(S,zeta,B0,B1):
	res = B0/n.sqrt(2*n.pi*S**3)*n.exp(-B0**2/2/S-B0*B1-B1**2*S/2)
	return res
def BFZH(S0,deltac,smin,K):
	return deltac-n.sqrt(2*(smin-S0))*K
def BFZHlin(S0,deltac,smin,K):
	b0 = deltac-K*n.sqrt(2*smin)
	b1 = K/n.sqrt(2*smin)
	return b0+b1*S0
def dlnBFdlnS0(S0,deltac,smin,K,d=0.001):
	Bp,Bo,Bm = BFZH(S0+d,deltac,smin,K), BFZH(S0,deltac,smin,K), BFZH(S0-d,deltac,smin,K)
	return S0/Bo*(Bp-Bm)/2/d
def dlnBFlindlnS0(S0,deltac,smin,K,d=0.001):
	Bp,Bo,Bm = BFZHlin(S0+d,deltac,smin,K), BFZHlin(S0,deltac,smin,K), BFZHlin(S0-d,deltac,smin,K)
	return S0/Bo*(Bp-Bm)/2/d

	##### m_min
dDoZ = n.load('theta.npz')
thetal,DoZl = dDoZ['arr_0'],dDoZ['arr_1']
ftheta = interp1d(DoZl,thetal,kind='cubic')
def theta(z,del0):
	return ftheta(del0/(1+z))
def RphysoR0(del0,z):
	th = theta(z,del0)
	return 3./10/del0*(1-n.cos(th))
def RcovEul(del0,z):
	return RphysoR0(del0,z)*(1+z)
def dlinSdlnR(lnR,d=0.001):
	res = (n.log(sig0(n.exp(lnR+d)))-n.log(sig0(n.exp(lnR-d))))/d/2
	return n.abs(res)




################################## MAIN ######################################

p.figure()
p.subplot(111)

for z in [12.,16.]:
	PLOT = True
	zeta = 40.
	K = scipy.special.erfinv(1-1./zeta)
	Tvir = 1.E4
	#z = 12.
	deltac = Deltac(z)
	mm = mmin(z)
	M0min = zeta*mm
	RLmin,R0min = m2R(mm), m2R(M0min)
	print 'R',RLmin
	smin = sig0(RLmin)
	Rmin = R0min*RcovEul(deltac,z)  #S0=smin, so del0=deltac; convertion from lagragian to comoving eulerian 
	####### FZH04 #######
	bFZH0 = deltac-K*n.sqrt(2*smin)
	bFZH1 = K/n.sqrt(2*smin)
	#bFZH = deltac-n.sqrt(2*(smin-S0))*K
	#bFZHlin = bFZH0+bFZH1*S0
	def dlnRdlnR0(lnR0,S0,del0):
		S0 = sig0(n.exp(lnR0))
		del0 = BFZH(S0,deltac,smin,K)
		th = theta(z,del0)
		thfactor = 1-3./2*th*(th-n.sin(th))/(1-n.cos(th))**2
		res = 1-dlinSdlnR(lnR0)*dlnBFdlnS0(S0,deltac,smin,K)*thfactor
		return res
	def V0dndlnR0(lnR0):
		S0 = sig0(n.exp(lnR0))
		return S0*fFZH(S0,zeta,bFZH0,bFZH1)*dlinSdlnR(lnR0)
	def VdndlnR0(lnR0):
		S0 = sig0(n.exp(lnR0))
		del0 = BFZHlin(S0,deltac,smin,K)
		#lnR0 = n.log(n.exp(lnR)/RcovEul(del0,z))
		
		VoV0 = (RcovEul(del0,z))**3
		#return VoV0/dlnRdlnR0(lnR0,S0,del0)*S0*fFZH(S0,zeta,bFZH0,bFZH1)*dlinSdlnR(lnR0)
		return VoV0*S0*fFZH(S0,zeta,bFZH0,bFZH1)*dlinSdlnR(lnR0)
	def VdndlnR(lnR0):
		S0 = sig0(n.exp(lnR0))
		del0 = BFZH(S0,deltac,smin,K)
		VoV0 = (RcovEul(del0,z))**3
		return VoV0/dlnRdlnR0(lnR0,S0,del0)*S0*fFZH(S0,zeta,bFZH0,bFZH1)*dlinSdlnR(lnR0)
	if True:
		print 'computing z=',z
		#Q = quad(lambda lnR: VdndlnR(lnR),n.log(Rmin),3.5)  #integrated over eulerian coordinates
		Q = quad(lambda lnR0: VdndlnR0(lnR0),n.log(R0min),3.5)  #integrated over eulerian coordinates
		print 'Q=',Q
		Q = Q[0]

		#######
		lnR0 = n.arange(n.log(R0min),3,0.03)
		S0list = []
		for lnr0 in lnR0: S0list.append(sig0(n.exp(lnr0)))
		S0list = n.array(S0list)
		#lnR = n.arange(n.log(Rmin),3,0.1)
		del0list = BFZH(S0list,deltac,smin,K)
		lnR = n.log(n.exp(lnR0)*RcovEul(del0list,z))

		normsize = []
		for lnr0 in lnR0:
			res = VdndlnR(lnr0)/Q
			print n.exp(lnr0),res
			normsize.append(res)
		p.semilogx(n.exp(lnR),normsize,label=str(z))

	
	if False:
		S0max = sig0(m2R(M0min))
		S0 = n.arange(0,S0max,0.2)
		bFZH = deltac-n.sqrt(2*(smin-S0))*K
		bFZHlin = bFZH0+bFZH1*S0
		p.plot(S0,bFZH,'b', label=str(z))
		p.plot(S0,bFZHlin,'b.-')
		p.ylim([0,20])
		p.xlim([0,25])


	
p.legend()
p.show()

################
# Z = float(opts.red)
# M0 = zeta*mmin(Z)*float(opts.mul)
# del0 = float(opts.del0)
###########################

# dlist = n.linspace(8,10,10)
# for del0 in dlist:
# 	res = fcoll_trapz_log(del0,M0,Z)
# 	print m2S(M0), res[0]
# if False:
# 	p.figure()
# 	p.plot(res[1],res[2])
# 	p.show()
	#tplquad(All,mm,M0,lambda x: 0, lambda x: 5., lambda x,y: gam(m2R(x))*y,lambda x,y: 10.,args=(del0,M0,z))

