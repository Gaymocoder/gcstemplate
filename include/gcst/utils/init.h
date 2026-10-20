#ifndef __GCST_UTILS_INIT_H__
#define __GCST_UTILS_INIT_H__

#include "gcst/utils/exstd.h"

namespace CLI { class App; }

namespace gcst
{
    namespace utils
    {
        gcst::etype init(int argc, char** argv, std::shared_ptr <CLI::App> lcli = nullptr);
    }

    using gcst::utils::init;
}

#endif