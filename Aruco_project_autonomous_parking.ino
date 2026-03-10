#include <AFMotor.h>


AF_DCMotor leftMotor1(1);  
AF_DCMotor leftMotor2(2);
AF_DCMotor rightMotor1(3); 
AF_DCMotor rightMotor2(4); 

char command;
int spd_0 = 110;
int currentSpeed = 0; 
int targetSpeed = 0;    
int turnSpeed = 90;   

void setup() {
  Serial.begin(9600);
  stopMotors();
}

void loop() {
  if (Serial.available()) {
    command = Serial.read();
    switch (command) {
      case 'F': 
        targetSpeed = spd_0;
        moveForward();
        break;
      case 'B': 
        targetSpeed = spd_0;
        moveBackward();
        break;
      case 'R':
        targetSpeed = turnSpeed;
        turnRight();
        break;
      case 'L':
        targetSpeed = turnSpeed;
        turnLeft();
        break;
      case 'S': 
        targetSpeed = 0;
        stopMotors();
        break;
    }
  }
  
  // Smooth PWM ramping
  updateSpeed();
}

void updateSpeed() {

  if (currentSpeed < targetSpeed) {
    currentSpeed += 2;  
    if (currentSpeed > targetSpeed) currentSpeed = targetSpeed;
  } else if (currentSpeed > targetSpeed) {
    currentSpeed -= 3; 
    if (currentSpeed < targetSpeed) currentSpeed = targetSpeed;
  }
  

  leftMotor1.setSpeed(currentSpeed);
  leftMotor2.setSpeed(currentSpeed);
  rightMotor1.setSpeed(currentSpeed);
  rightMotor2.setSpeed(currentSpeed);
  
  delay(10);  
}

void moveForward() {
  leftMotor1.run(FORWARD);
  leftMotor2.run(FORWARD);
  rightMotor1.run(FORWARD);
  rightMotor2.run(FORWARD);
}

void moveBackward() {
  leftMotor1.run(BACKWARD);
  leftMotor2.run(BACKWARD);
  rightMotor1.run(BACKWARD);
  rightMotor2.run(BACKWARD);
}

void turnLeft() {
  leftMotor1.run(BACKWARD);
  leftMotor2.run(BACKWARD);
  rightMotor1.run(FORWARD);
  rightMotor2.run(FORWARD);
}

void turnRight() {
  leftMotor1.run(FORWARD);
  leftMotor2.run(FORWARD);
  rightMotor1.run(BACKWARD);
  rightMotor2.run(BACKWARD);
}

void stopMotors() {
  leftMotor1.run(RELEASE);
  leftMotor2.run(RELEASE);
  rightMotor1.run(RELEASE);
  rightMotor2.run(RELEASE);
}