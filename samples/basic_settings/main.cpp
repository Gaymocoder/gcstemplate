#include <print>

#include <gcst/gcst.h>

int main(int argc, char** argv)
{
    if (auto r = gcst::settings::init(argc, argv); !r)
        return r.error();

    std::println("file-loglevel: {}", gcst::params->get("file-loglevel"));
}