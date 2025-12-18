void setup() {
  Serial.begin(115200);
}

void loop() {
  int x = analogRead(A0);

  // format tipo "valore valore"
  Serial.println(x);
}