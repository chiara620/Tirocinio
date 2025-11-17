void setup() {
  Serial.begin(115200);
}

void loop() {
  int t0 = analogRead(A0);
  int t1 = analogRead(A2); 

  // format tipo "valore valore"
  Serial.print(t0);
  Serial.print(" ");
  Serial.println(t1);
}