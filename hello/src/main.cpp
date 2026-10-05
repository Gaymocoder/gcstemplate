#include <gcst/gcst.h>

#include "gcst/showcase.h"

int main(int argc, char** argv)
{
    if (!gcst::settings::init(argc, argv))
        return 1;
        
    gcst::showcase::test_cli();
    return 0;
}