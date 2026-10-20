#include "gcst/utils/init.h"

#include <spdlog/spdlog.h>
#include <spdlog/sinks/sink.h>

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

    INFO("gcstemplate has been inited succesfully");
    DEBUG("Parsed options:");
    gcst::params->debug();

    INFO("gcst::journal is inited with logfile {}", gcst::journal->relfilepath().string());
    DEBUG("  journal's file loglevel '{}'", gcst::journal->filesink()->level());
    DEBUG("  journal's console loglevel: '{}'", gcst::journal->consolesink()->level());
    return 0;
}

}