from brian2 import *
from random import gauss

# Create a new "Leaky integrate-and-ﬁre" NeuronGroup (with refraction and inhibition)
genNeurons(nbNeurons, threshold, reset, tRefrac):
    eqs = '''dv/dt = -v/tLeak : volt (unless refractory)
             lastInhib : second'''

    neurons = NeuronGroup(nbNeurons, eqs, threshold='v >= threshold',
        reset='v = 0*volt', refractory=tRefrac)

    return neurons

# Create synapses between pre and post following connectionRule
genSynapses(pre, nbPre, post, nbPost, connectionRule, wAverage, wDeviation, wMin, wMax,
        aPre, aPost, bPre, bPost, tLTP, tLeak, tInhib):
    synapsesModel = '''w : volt
                   dwPre = aPre * exp(-bPre*(w-wMin/wMax-wMin)) : volt
                   dwPost = aPost * exp(-bPost*(wMax-w/wMax-wMin)) : volt
                   tPre : second
                   tPost : second
                   ltpCondition = tPost > tPre and (tPost - tPre) <= tLTP : 1'''

    preEqs = '''tPre = t
            v = v * (t - lastInhib < tInhib and lastInhib != 0 * ms) + (v * exp(-(t-lastupdate)/tLeak) + w) * (t - lastInhib >= tInhib or lastInhib == 0 * ms)'''

    postEqs = '''tPost = t
             w = clip(w + dwPre * (tPre != 0 * second and ltpCondition), wMin, wMax)
             w = clip(w - dwPost * (tPre == 0 * second or ltpCondition == 0), wMin, wMax)'''

    synapses = Synapses(pre, target=post, model=synapsesModel, pre=preEqs, post=postEqs)
    synapses.connect(connectionRule) # Connecting every neurons of the first layer to every neurons of the second one

    for i in range(nbPre):
        for  j in range(nbPost):
            synapses.w[i,j] = clip(
                gauss(wAverage, wDeviation),
                wMin,
                wMax)

    return synapses

# Create inhibition on layer
genInhibition(layer, tRefrac):
    inhibition = Synapses(layer, target=layer, model='', pre='''
        lastInhib = (lastupdate + tRefrac) * (1 - int(not_refractory)) + t * int(not_refractory)''')

    inhibition.connect("i != j")

    return inhibition
