#include "mylogger.h"

int main(int argc, char** argv)
{
    if (auto r = gcst::settings::init(argc, argv); !r)
        return r.error();

    // Same init as gcst::logger has, but with mylogger's sinks and patterns
    if (auto l = mylogger::init(); !l)
        return l.error();

    TRACE("This is a trace message");
    DEBUG("This is a debug message");
    INFO("This is an info message");
    WARN("This is a warn message");
    ERROR("This is an error message");
    CRITICAL("This is a critical message");

    // Console shows short records, the file keeps detailed ones
    INFO("Detailed log: {}", gcst::journal->filepath().string());
}
