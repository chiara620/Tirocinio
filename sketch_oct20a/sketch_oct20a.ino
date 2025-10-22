void setup() {
  Serial.begin(115200);
}

void loop() {
  int t0 = analogRead(A0);
  int t1 = analogRead(A1);

  // formato tipo "A0:[valore],A1:[valore]"
  Serial.print("A0:");
  Serial.print(t0);
  Serial.print(",A1:");
  Serial.println(t1);

  delay(100);
}
