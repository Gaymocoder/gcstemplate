#include <gcst/gcst.h>

int main(int argc, char** argv)
{
    if (auto result = gcst::init(argc, argv); !result)
        return result.error();
        
    INFO("Hello world!");
    return 0;
}