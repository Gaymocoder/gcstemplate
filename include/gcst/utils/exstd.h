#ifndef __GCST_UTILS_EXST__
#define __GCST_UTILS_EXST__

#include <expected>
#include <filesystem>

namespace fs = std::filesystem;

namespace gcst
{
    namespace utils
    {
        namespace exstd
        {
            typedef std::expected <int, int> etype;

            fs::path exe_path();
        }

        using namespace gcst::utils::exstd;
    }

    using gcst::utils::etype;
}

#endif