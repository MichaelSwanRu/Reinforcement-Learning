import math
import pandas as pd
import numpy as np


################  MODEL PARAMETERS  ###################
# Расстояния до стены от которой должны отойти на максимальное расстояние
distanceNew = 0.0;   # Текущее расстояние от стены
distanceOld = 200.0; # Начальное расстояние от стены
deltaDistance = 0.0; # Изменение расстояния от стены


numTheta1States = 6;
theta1InitialAngle = 100.0;
theta1Max = 100.0;                          
theta1Min = 80.0;
deltaTheta1 = (theta1Max - theta1Min)/(float(numTheta1States)-1.0);    
s1 = int((theta1InitialAngle - theta1Min)/deltaTheta1);   

numTheta2States = 6;
theta2InitialAngle = 160.0;                
theta2Max = 160.0;   
theta2Min = 90.0;
deltaTheta2 = (theta2Max - theta2Min)/(float(numTheta2States)-1.0); 
s2 = int((theta2InitialAngle - theta2Min)/deltaTheta2);

numStates = numTheta1States*numTheta2States;
numActions = 4;
Q = pd.DataFrame(index=np.arange(numStates), columns=np.arange(numActions))
s = int(s1*numTheta2States + s2);
sPrime = s;

explorationConst = 300
gamma = 0.75;      
alpha = 0.1;
r = 0.0;
lookAheadValue = 0.0;
sample = 0.0;
s01 = s1; s02 = s2;
################  MODEL PARAMETERS  ###################


################  MODEL ACTIONS  ###################

def initializeQ():
    for i in range(numStates):
        for j in range(numActions):
            Q.iloc[i,j] = 10.0;
            

def ultrasonic_ping():
    global s01, s02, distanceOld, current_action   
    A = 0    
    if (current_action == 2): 
        if (s01 == 0): 
            if (s02 == 0):
                A = -1
    if (current_action == 3): 
        if (s01 == 0): 
            if (s02 == 1):
                A = 1
    return distanceOld + A


def getDeltaDistanceRolled():
    global distanceOld, distanceNew, deltaDistance 
    distanceNew = float(ultrasonic_ping());   
    deltaDistance = distanceNew - distanceOld;
    distanceOld = distanceNew;
    return deltaDistance;



def getAction():
    global s1, s2, numTheta1States, numTheta2States, s, epsilon  
    valMax = -10000000.0;
    aMax = -100
    randomActionFound = False;
    allowedActions = [-1, -1, -1, -1]; 
    if ((s1 + 1) != numTheta1States):
       allowedActions[0] = 1;
       val = Q.iloc[s, 0];
       if(val > valMax):
           valMax = val;
           aMax = 0;
    if(s1 != 0):
       allowedActions[1] = 1;
       val = Q.iloc[s, 1];
       if(val > valMax):
           valMax = val;
           aMax = 1;
    if((s2 + 1) != numTheta2States):
        allowedActions[2] = 1;
        val = Q.iloc[s, 2];
        if(val > valMax):
            valMax = val;
            aMax = 2;
    if(s2 != 0):
        allowedActions[3] = 1;
        val = Q.iloc[s, 3];
        if(val > valMax):
            valMax = val;
            aMax = 3;
    randVal = np.random.randint(0,101,1)[0];    
    if (randVal < (1.0-epsilon)*100.0):    
        action = aMax;
    else:
        while (randomActionFound == False):
            action = np.random.randint(0,3,1)[0];
            if(allowedActions[action] == 1):
                randomActionFound = True;
    return(action);


def setSPrime(action):
    global s, numTheta2States, s1, s2, sPrime
    if (action == 0):
        sPrime = s + numTheta2States;
    if (action == 1):
        sPrime = s - numTheta2States;
    if (action == 2):
        sPrime = s + 1;
    if (action == 3):
        sPrime = s - 1;


def getLookAhead():
    global numTheta1States, numTheta2States, sPrime , s1, s2
    valMax = -100000.0;
    if((s1 + 1) != numTheta1States):
        val = Q.iloc[sPrime, 0];
        if(val > valMax):
            valMax = val;
    if(s1 != 0):
        val = Q.iloc[sPrime, 1];
        if(val > valMax):
            valMax = val;
    if((s2 + 1) != numTheta2States):
        val = Q.iloc[sPrime, 2];
        if(val > valMax):
            valMax = val;
    if(s2 != 0):
        val = Q.iloc[sPrime, 3];
        if(val > valMax):
            valMax = val;
    return valMax;


def setPhysicalState(action):
    global s1, s2
    if (action == 0):
        s1 += 1;
    if (action == 1):
        s1 -= 1;
    if (action == 2):
        s2 += 1;
    if (action == 3):
        s2 -= 1;
###############  MODEL ACTIONS  ###################



minus = 0;
plus = 0;

initializeQ();
for t in range(1,15000):
    epsilon = math.exp(-float(t)/explorationConst); 
    s01 = s1; s02 = s2
    current_action = getAction(); 
    setSPrime(current_action);  
    setPhysicalState(current_action);
    r = getDeltaDistanceRolled(); 
    lookAheadValue = getLookAhead();   
    sample = r + gamma*lookAheadValue;
    if t > 14900:    
        print 'Time: %(0)d, was: %(1)d %(2)d, action: %(3)d, now: %(4)d %(5)d, prize: %(6)d ' % \
            {"0": t, "1": s01, "2": s02, "3": current_action, "4": s1, "5": s2, "6": r}        
    Q.iloc[s, current_action] = Q.iloc[s, current_action] + alpha*(sample - Q.iloc[s, current_action] ) ;
    s = sPrime;
    if deltaDistance == 1: 
        plus += 1;
    if deltaDistance == -1: 
        minus += 1;
    if (t == 2):
        initializeQ();
print( minus, plus)





