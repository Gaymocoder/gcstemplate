#ifndef __GCST_UTILS_EXST__
#define __GCST_UTILS_EXST__

#include <filesystem>

namespace fs = std::filesystem;

namespace gcst::utils::exstd
{
    fs::path exe_path();
}

#endif