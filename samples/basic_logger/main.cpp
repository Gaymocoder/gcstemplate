#include <gcst/gcst.h>

int main(int argc, char** argv)
{
    if (auto result = gcst::init(argc, argv); !result)
        return result.error();

    TRACE("This is a trace message");
    DEBUG("This is a debug message");
    INFO("This is an info message");
    WARN("This is a warn message");
    ERROR("This is an error message");
    CRITICAL("This is a critical message");
}