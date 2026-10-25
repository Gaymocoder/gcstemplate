#include <iostream>

#include <gcst/gcst.h>

int main(int argc, char** argv)
{
    if (auto r = gcst::settings::init(argc, argv); !r)
        return r.error();

    std::cout << "file-loglevel: " << gcst::params->get("file-loglevel").value();
}