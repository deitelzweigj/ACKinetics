# ACKinetics
This is for the code used at my ACKinetics internship where we use image tracking to move a hoop to catch a ball.

The Arduino code is controlling a stepper motor. It will accelerate the motor to reach top speed and move it to the point it recieves from serial.

The Python code is recieving input from a webcam and using OpenCV to find the location of a green ball and its linear trajectory and then send it to the arduino through serial

Install OpenCV using `pip install opencv-python`
