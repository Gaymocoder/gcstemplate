#include <print>

#include "mysettings.h"

int main(int argc, char** argv)
{
    if (auto r = mysettings::init(argc, argv); !r)
        return r.error();

    // After successful initializaton parsed params are stored in gcst::params
    std::println("Port: {}", gcst::params->get("port"));
    std::println("Level: {}", gcst::params->get("level"));
}