# PJI

### Requirements
* Python 2.7
* Brian2 Simulator

### MovementLearningScript
Creates a neuronal system able to recognize a vertical movement between n pixels. It takes parameters at execution to init some variables.
The parameters are the following :
* -i or --inhibition = Specify inhibition time in ms. Required.
* -l or --leak = Specify leak time in ms. Required.
* -n or --number = Specify number of learning test iterations. 100 iterations by defaults, integers only.
* -r or --refraction = Specify refraction time in ms. Required.
* -s = Defines if the learning is supervised or not. Default = False

At end of execution, it will print the number of successful tries

### MovementRecognition
This script will create a neuronal system able to recognize a vertical movement between 2 pixels. Then, it will redistribute the synapse weight to a new neuronal system able to recognize a vertical movement between n pixels
This script has one parameters : -s = Defines if the learning is supervised or not. Default = False

### nPxMovementRecognition
Creates a neuronal system able to recognize a vertical movement between n pixels. The variables are given with parameters :
* -i or --inhibition = Specify inhibition time in ms. Required.
* -l or --leak = Specify leak time in ms. Required.
* -r or --refraction = Specify refraction time in ms. Required.
* --ltp = Specify ltp time in ms. Required.
* -t or --threshold = Specify threshold value in volt. Required.
* -s or --supervised= Defines if the learning is supervised or not. Default = False
* --random = Specify if the pattern are introduced in a random order.
* -n or --number = Specify number of learning test iterations. 100 iterations by defaults, integers only.
