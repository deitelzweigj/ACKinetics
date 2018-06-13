#include <TimerOne.h>


// Define constants
const int PUL_PIN   = 7;  //pulse pin
const int DIR_PIN   = 6;  //direction pin
const int ENA_PIN   = 5;  //enable pin
const int LIMIT_PIN = 2;  // Limit switch on track
#define BAUD_RATE       115200

//---- Stepper Motor related variables 
long unsigned int goalPos = 0;
long unsigned int currPos = 0;
int   startDelay  = 50;      // starting speed 
int   minDelay    = 1;      // max speed 
float startAccel       = 0.0125;    // works with 0.6 accel and 4e can travel
int   isrCalled   = 0;       // flag

const int         arrayLength = 10;
long unsigned int goalCmds[arrayLength] = {0};
int               arrayIndex = 0;
long unsigned int arraySum   = 0;
long unsigned int arrayAvg   = 0;

int serialFlag=0;
int dirToMove=0;
int moveAmount=0;
static float currentDelay = startDelay;
static float accel = startAccel;
int maxPosition=23000;

// setup function. Runs once
void setup(){
  pinMode(PUL_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(ENA_PIN, OUTPUT);
  pinMode(LIMIT_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(LIMIT_PIN), isrReset, RISING);  // on a state change, run the rest function
  //Timer1.initialize(10000000000);
  //Timer1.attachInterrupt(movement);

  Serial.begin(BAUD_RATE);
  Serial.println("Ready");
  reset();
}// End setup()  


//------------ Main Loop
void loop(){
  reading();
  //for(int i=0;i<6400;i++){movement();if(abs(moveAmount)<=500){break;}}
  movement();
}//------------ End of Main()
void reading(){
  //---  Read Serial cmds, cap/floor value, and filter -----
  if(Serial.available()>0){//&&serialFlag>=100){
    goalPos = Serial.parseInt();                      // up to 32,767
//    Serial.print("Received: "); Serial.println(goalPos);
    goalPos = constrain(goalPos, 0, maxPosition);     // set max and min vals
      
//    arraySum = arraySum - goalCmds[arrayIndex];       // subtract last reading 
//    goalCmds[arrayIndex] = goalPos;                   // add new cmd
//    arraySum = arraySum + goalCmds[arrayIndex];       // add new reading 
//    if(arrayIndex++ > arrayLength) {arrayIndex = 0;}  // advance array and wrap around if needed
//    arrayAvg = arraySum/arrayLength;                  
    
    if (Serial.read() == '\n') {serialFlag=0;}

  }// end Serial.available()


  
  serialFlag++;
  
}
void movement(){
  //--- Determine how much to move ---------
  moveAmount = (goalPos - currPos);        // error in position. TODO: replace goalPos with arrayAvg
  int tempDirToMove  = (moveAmount >=0 ) ? 0:1;    // pick direction
  if(dirToMove-tempDirToMove != 0){currentDelay=startDelay;accel=startAccel;} // If changing direction, restart acceleration
  
  dirToMove=tempDirToMove;

  if( abs(moveAmount) >= 500){                  // move stage if we're outside error threshold
   currentDelay = (currentDelay > minDelay) ? (currentDelay - accel):(minDelay);
   accel+=0.00001;
   turn(dirToMove, currentDelay);             // inc or dec currPos
             
  }else{        // we're close to our goalPos. Don't turn(), reset currentDelay
    currentDelay = startDelay;
    accel = startAccel;
    
  }
}
// ---- Steps the motor once in specified direction
inline void turn(int dir, int motorDelay){ //0(right) or 1(left) to change direction
  digitalWrite(DIR_PIN, dir);       //TODO: Should be set outside the step. 0x1:HIGH,0x0:LOW
  digitalWrite(ENA_PIN, HIGH);
  digitalWrite(PUL_PIN, HIGH);
  delayMicroseconds(motorDelay);
  digitalWrite(PUL_PIN, LOW);
  delayMicroseconds(motorDelay);
  currPos -= 2*dir-1;                 //if(dir=1) currPos -= 1. if(dir=0) currPos -= -1
//  currPos = currPos + ((dir == 1) ? -1:1 );   // more readable? TODO: test
} //-- End of turn()


// turns motor X steps. ** blocks other inputs until steps are complete ***
//void stepXTurns(int dir, int numOfSteps){
//  float localMicroDelay = startDelay;
//  digitalWrite(DIR_PIN, dir);  
//  
//  for(int i = 0; i < numOfSteps-1; i++){        // blocks new inputs
//   localMicroDelay = (localMicroDelay > minDelay) ? (localMicroDelay - accel):(minDelay); //TODO: Test if this works
//   turn(dir, int(localMicroDelay));
//  }  
//} // End stepXTurns()

//---- reset() gets called at setup(). Runs once
void reset(){  
  Serial.println("Moving left...");
  while(isrCalled == 0 ){             // isrCalled = 1 when isrReset gets called
    turn(1, 200);                      // turn 'left' at speed of 50
  }// we're at the left limit switch. isrReset() has been called
}// End of reset()

// --- isrReset() is called by the interrupt routine. When LIMIT_PIN goes from LOW to HIGH
void isrReset(){
  Serial.println("Resetting...");
  isrCalled = 1;      
  currPos   = 0;          // reset stuff
//  stepXTurns(0, 2000);    // Moving stage to the middle... This will be the 0 point
  for(int i = 0; i < 500; i++){        // blocks new inputs
   turn(0, 200);
  }
  
  goalPos   = currPos;    // zero the stage at current position (ie. 2000) 
}//-- End of isrRest()

