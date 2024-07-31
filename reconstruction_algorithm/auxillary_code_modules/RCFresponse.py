import numpy as np
"LET correction simulations in scintillator"




def underesponse(S,a,b):  #we need the dose weighted LET
    ''' linear model for under responde '''
    return (a*S)+b


def rcfdosecorrection(rcfdose,S,a,b):
    '''rcf measurements / linear trend '''

    return np.divide(rcfdose, underesponse(S,a,b), out=np.zeros_like(rcfdose),
                                                where= underesponse(S,a,b)!=0 )

def rcfcorrection(rcfdepth,rcfdose,rcferr,depth_sci,LET_zdoseprofile,a,b,s):
    S=np.interp(np.arange(0,len(rcfdose),1)*s,depth_sci,LET_zdoseprofile)
    D_rcf=rcfdosecorrection(rcfdose,S,a,b)
    Derr_rcf=rcfdosecorrection(rcferr,S,a,b)
    area_rcfcorrected=np.trapz(rcfdosecorrection(rcfdose,S,a,b),rcfdepth)
    return D_rcf,Derr_rcf,area_rcfcorrected
