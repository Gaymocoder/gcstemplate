#ifndef __GCST_UTILS_BASIC_LOGGER_TPP__
#define __GCST_UTILS_BASIC_LOGGER_TPP__

#include <memory>

#include "gcst/utils/settings.h"
#include "gcst/utils/basic_logger.h"

namespace gcst::utils
{

template <class dlogger>
template <class... Args>
gcst::etype basic_logger <dlogger> ::init(Args&&... args)
{
    if (!GCST_SETTINGS_INITED)
        return std::unexpected(1);

    auto lfparam = gcst::params->get("logfile-name");
    if (!lfparam) return std::unexpected(2);
        
    auto ldparam = gcst::params->get("logdir-path");
    if (!ldparam) return std::unexpected(3);

    fs::path lfiledir = std::string(*ldparam);
    std::string lfilename = std::string(*lfparam);

    auto ljournal = std::make_unique <enabler> (lfiledir, lfilename, std::forward <Args> (args)...);
    if (!ljournal->setup()) return std::unexpected(4);
    
    gcst::journal = std::move(ljournal);
    return 0;
}

}

#endif