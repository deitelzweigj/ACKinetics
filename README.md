# ACKinetics
This is for the code used at my ACKinetics internship where we use image tracking to move a hoop to catch a ball.
The arduino code is controlling a stepper motor. It will accelerate the motor to reach top speed and move it to the point it recieves from serial.
The python code is recieving input from a webcam and using openCV to find the location of a green ball and its linear trajectory and then send it to the arduino through serial
Install openCV using pip it is under the name opencv-python //<--check this
