int f(int a) {
  int i;
  int s;
  s = 0;
    for(i = 0; i < a; i++) {
      s += i;
    }
    while(s > 0) {
      s -= 1;
    }
  return s;
}