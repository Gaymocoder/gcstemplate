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

    auto lfparam = gcst::params->get("logfile");
    std::string lfilename = lfparam ? std::string(*lfparam) : gcst::utils::strnow() + ".gcstlog";

    gcst::journal = std::make_unique <enabler> (lfilename, std::forward <Args> (args)...);
    return 0;
}

}

#endif