from brian2 import *
from random import gauss

# Create a new "Leaky integrate-and-fire" NeuronGroup (with refraction and inhibition)
def genNeurons(nbNeurons):
    eqs = '''dv/dt = -v/tLeak : volt (unless refractory)
             lastInhib : second
             thresh : volt
             tLeak : second
             tRefrac : second
             tInhib : second
             vMax = nanmax(v/volt) * volt: volt
             activated : 1'''

    neurons = NeuronGroup(nbNeurons, eqs, threshold='(v*tLeak/(tLeak-dt)) >= thresh and v == vMax', reset='v = 0*volt', refractory='tRefrac')
    neurons.activated = 1

    return neurons

# Create synapses between pre and post following connectionRule
def genSynapses(pre, nbPre, post, nbPost, connectionRule, wAverage, wDeviation, wMin, wMax, needActivation = False, begin = 0):
    synapsesModel = '''w : volt
                   dwPre = aPre * exp(-bPre*(w-wMin/wMax-wMin)) : volt
                   dwPost = aPost * exp(-bPost*(wMax-w/wMax-wMin)) : volt
                   tPre : second
                   tPost : second
                   tLTP : second
                   ltpCondition = tPost > tPre and (tPost - tPre) <= tLTP : 1'''

    if needActivation:
        preEqs = '''tPre = t
                v_post += (w * int((t - lastInhib_post >= tInhib or lastInhib_post == 0 * ms) and not_refractory)) * activated_post
                activated_post = 0'''
    else:
        preEqs = '''tPre = t
                v_post += w * int((t - lastInhib_post >= tInhib or lastInhib_post == 0 * ms) and not_refractory)
                activated_post = 1'''

    postEqs = '''tPost = t
             w = clip(w + dwPre * int(tPre != 0 * second and ltpCondition), wMin, wMax)
             w = clip(w - dwPost * int(tPre == 0 * second or ltpCondition == 0), wMin, wMax)'''

    synapses = Synapses(pre, target=post, model=synapsesModel,
        pre=preEqs, post=postEqs)
    synapses.connect(connectionRule)

    for i in range(nbPre):
        for  j in range(nbPost):
            synapses.w[i,j] = clip(
                gauss(wAverage, wDeviation),
                wMin,
                wMax)

    return synapses

# Create inhibition on layer
def genInhibition(layer):
    inhibition = Synapses(layer, target=layer, model='', pre='''
        lastInhib_post = t
        v_post -= v_post''')

    inhibition.connect("i != j")

    return inhibition
