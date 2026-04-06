int relay1 = 2;
int relay2 = 3;
int relay3 = 4;
int relay4 = 5;

void setup() 
{ 
  Serial.begin(9600); 
  pinMode(relay1,OUTPUT); 
  pinMode(relay2,OUTPUT); 
  pinMode(relay3,OUTPUT); 
  pinMode(relay4,OUTPUT); 
  digitalWrite(relay1, HIGH);
  digitalWrite(relay2, HIGH);
  digitalWrite(relay3, HIGH);
  digitalWrite(relay4, HIGH);
  Serial.println("Ready");
}

void loop()
{
  if(Serial.available() > 0){
    String status = Serial.readString();
    status.trim();
    if (status == "one_off"){
      digitalWrite(relay1, HIGH); 
    }
    else if (status == "one_on"){
      digitalWrite(relay1, LOW);
    }
    else if (status == "two_off"){
      digitalWrite(relay2, HIGH); 
    }
    else if (status == "two_on"){
      digitalWrite(relay2, LOW);
    }
    else if (status == "three_off"){
      digitalWrite(relay3, HIGH); 
    }
    else if (status == "three_on"){
      digitalWrite(relay3, LOW);
    }
    else if (status == "four_off"){
      digitalWrite(relay4, HIGH); 
    }
    else if (status == "four_on"){
      digitalWrite(relay4, LOW);
    }
  } 
}