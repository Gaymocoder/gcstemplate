#include <iostream>

#include "mysettings.h"

int main(int argc, char** argv)
{
    if (auto r = mysettings::init(argc, argv); !r)
        return r.error();

    // After successful initializaton parsed params are stored in gcst::params
    std::cout << "Port: {}" << gcst::params->get("port").value();
    std::cout << "Level: {}" << gcst::params->get("level").value();
}