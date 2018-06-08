const int PUL=7;//pulse pin
const int DIR=6;//direction pin
const int ENA=5;//enable pin
const int leftPin=2;
int switchState=0;
int testDelay=100;
int moveDelay=35;
int resetDelay=200;
long int baud=115200;
int d=3;
int target=0;
int ball=0;
int dist=0;
int l=50;
int stepsPerRotation=6400;
int stepLength=l/(PI*d)*stepsPerRotation;
long int frames=0;

void setup(){
  pinMode(PUL, OUTPUT);
  pinMode(DIR, OUTPUT);
  pinMode(ENA, OUTPUT);
  Serial.begin(baud);
  Serial.println("ready");
  reset();
}
void loop(){
  //reset();
  //moveTest();
  move();
}
void moveTest(){
  for(int i=0;i<stepsPerRotation;i++){//one rev and end
    turn(0, testDelay);
  }
  exit(0);
}
void move(){
  setBall();
  int E=0;
  do{
    E++;
    dist=target-ball;
    switchState=digitalRead(leftPin);
    if(switchState==HIGH){reset();break;}
    //Serial.println("Target: "+dist);
    int dir;
    if(dist>=0){dir=1;}//left
    else if(dist<0){dir=0;}//right
    //if(ball<=stepLength&&ball>=0)
      if(abs(dist)>=1000)
        turn(dir, moveDelay);
  }
  while(abs(dist)>=1000&&E<=6400);
}
void setBall(){
    if(Serial.available()>0){
      ball=Serial.parseInt();//HERE
      frames++;
      if(frames%1==0){
        Serial.print("Received: ");
        Serial.println(ball, DEC);
      }
    }
}
void turn(int dir, int motorDelay){//0(right) or 1(left) to change direction
  digitalWrite(DIR, dir);//0x1:HIGH,0x0:LOW
  digitalWrite(ENA, HIGH);
  digitalWrite(PUL, HIGH);
  delayMicroseconds(motorDelay);
  digitalWrite(PUL, LOW);
  delayMicroseconds(motorDelay);
  target-=2*dir-1;//1 if 1, -1 if 0
}
void reset(){
  //Serial.println("moving left");
  while(switchState==LOW){
    switchState = digitalRead(leftPin);
    turn(1, resetDelay);
    /*digitalWrite(DIR,HIGH);
    digitalWrite(ENA,HIGH);
    digitalWrite(PUL,HIGH); //Trigger one step forward
    delayMicroseconds(motordelay);
    digitalWrite(PUL,LOW); //Pull step pin low so it can be triggered again
    delayMicroseconds(motordelay);*/
  }
   target=0;
  //Serial.println("moving right");
  delay(2);
  for(int k=11950; k > 0 ; k--){
    turn(0, resetDelay);
    /*digitalWrite(DIR,LOW);
    digitalWrite(ENA,HIGH);
    digitalWrite(PUL,HIGH); //Trigger one step forward
    delayMicroseconds(motordelay);
    digitalWrite(PUL,LOW);
    delayMicroseconds(motordelay);*/
  }
  //position1 = 11720;
  //Serial.println("reset complete");
  //Serial.println("Enter new option");
  //Serial.println();
  
}

