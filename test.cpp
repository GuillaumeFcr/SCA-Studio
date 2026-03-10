#include <iostream>
#include "Install 1.9.20/bps202.h"
using namespace std;

int main() {
    DLL::bps_init();
    char*e=DLL::bps_get_probename();
    cout<< *e << endl;
    return 0;
}
