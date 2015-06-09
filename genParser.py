from optparse import OptionParser
from brian2 import *

# Create a generic parser for neural system simulation
def genParser():
    parser = OptionParser()

    parser.add_option("-i", "--inhibition",
        help='''Specify inhibition time in ms. Required.''')

    parser.add_option("-l", "--leak",
        help='''Specify leak time in ms. Required.''')

    parser.add_option("-r", "--refraction",
        help='''Specify refraction time in ms. Required.''')

    parser.add_option("--ltp",
        help='''Specify ltp time in ms. Required.''')

    parser.add_option("-t", "--threshold",
        help='''Specify threshold value in volt. Required.''')

    parser.add_option("-s", "--supervised", action="store_true",
        help='''Specify the kind of learning (supervised or not).''',
        default=False)

    parser.add_option("--random", action="store_true",
        help='''Specify if the pattern are introduced in a random order.''',
        default=False)

    parser.add_option("-n", "--number",
        help='''Specify number of learning test iterations.\r\n
            1 iteration by default, integers only.''',
        default=1)

    return parser

# Return args from option parser
def getArgs(parser):
    (options, args) = parser.parse_args()

    try :
        tInhib = float(options.inhibition) * ms
        tLeak = float(options.leak) * ms
        tRefrac = float(options.refraction) * ms
        tLTP = float(options.ltp) * ms
        threshold = float(options.threshold) * volt
        supervised = options.supervised
        randomPattern = options.random
        nIter = int(options.number)
    except :
        print "Error : Invalid argument. See help for more informations."
        parser.print_help()
        exit(False)

    return {'tInhib':tInhib, 'tLeak':tLeak, 'tRefrac':tRefrac, 'tLTP':tLTP,
        'threshold':threshold, 'supervised':supervised,
        'randomPattern':randomPattern, 'nIter':nIter}
