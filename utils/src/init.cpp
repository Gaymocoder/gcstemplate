#include "gcst/utils/init.h"

#include "gcst/utils/logger.h"
#include "gcst/utils/settings.h"

namespace gcst::utils
{
    
gcst::etype init(int argc, char** argv, std::shared_ptr <CLI::App> lcli)
{
    if (auto result = gcst::settings::init(argc, argv, lcli); !result)
        return std::unexpected(1);

    if (auto result = gcst::logger::init(); !result)
        return std::unexpected(2);

    return 0;
}

}