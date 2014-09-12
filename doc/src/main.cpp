#include <iostream>
#include "lib.h"
using namespace std;

int main(){
  Squared<double> s;
  cout << s(4) << endl;
  return 0;
}
