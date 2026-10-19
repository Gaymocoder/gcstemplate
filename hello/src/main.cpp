#include <gcst/gcst.h>

#include "gcst/showcase.h"

int main(int argc, char** argv)
{
    if (!gcst::settings::init(argc, argv))
        return 1;

    if (!gcst::logger::init())
        return 2;
        
    gcst::showcase::test_cli();
    return 0;
}