# PJI

### Requirements
* Python 2.7
* Brian2 Simulator

### MovementLearningScript
This script creates neural networks which goal is to be able to recognize a vertical movement between 2 pixels. These networks, based on parameters given as arguments, will learn to detect these movements with supervised or unsupervised learning. At the end, the script counts the number of successful learning and print it to the user.

The arguments, taken at execution, are the following :
* -i or --inhibition = Specify inhibition time in ms. Required.
* -l or --leak = Specify leak time in ms. Required.
* -n or --number = Specify number of learning test iterations. 100 iterations by defaults, integers only.
* -r or --refraction = Specify refraction time in ms. Required.
* -s or --supervised = Defines if the learning is supervised or not. Default = False

This script uses old neural network, therefore it's not fully working.

### MovementRecognition
This script creates a neural network which goal is to be able to recognize a vertical movement between n pixels. Firstly, it will create a neural network able to recognize a vertical movement between 2 pixels. Then, it will redistribute synapses weight to a new network able to recognize a vertical movement between n pixels. If networks are unable to recognize a movement, the learning is reset until it does.

This script take one arguments at execution : -s = Defines if the learning is supervised or not. Default = False

This script uses old neural network, therefore it's not fully working.

### nPxMovementRecognition
This script creates a neural network which goal is to be able to recognize a vertical movement between n pixels with unsupervised learning. In order to reach its goal, this network will take two following movements, in the same direction (up or down), and recognize it as a bigger movement. This step is repeat until there is only 4 movements left (2 up and 2 down). Then the network will recognize the final movements depending on these 4 movements.

This script uses the files genXXX.py. These files are used to simplify the main code and the creation of inputs, neurons and synapses.

##### genInput
This file helps the creation of input :
* createPatterns : Creates an up or down movement depending of the number of pixels
* genAlternateVerticalMovements : Creates a SpikeGeneratorGroup with alternate up and down movements. nbPatterns give the number of movements generated.  
* genRandomVerticalMovements : Creates a SpikeGeneratorGroup with equally randomized up and down movements. nbPatterns give the number of movements generated

##### genLayer
This file helps the creation of neurons and layer :
* genNeurons : Creates a new "Leaky integrate-and-fire" NeuronGroup (with refraction and inhibition)
* genSynapses : Creates synaptic connection between pre and post following connectionRule
* genInhibition : Creates inhibited synaptic connection between every neuron of layer.
