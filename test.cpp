#include <iostream>
#ifdef __cplusplus
extern "C" {
#endif
#include "bps202.h"

int main() {
	double* b = new double;
    int a=bps_init();
	while (bps_get_status()==-1){}
	std::cout << "connecte"<<std::endl;
	std::cout << bps_get_pulse_level_count()<<std::endl;
    int e=bps_get_pulse_levels(b,46);
	std::cout << bps_get_pulse_range_count()<<std::endl;
	std::cout<<e;
	std::cout << std::endl;
	for (int i=0;i<46;i++){
		std::cout<< *(b+i)<<" ";
	}
	std::cout<<std::endl;
    return 0;
}

#ifdef __cplusplus
}
#endif
