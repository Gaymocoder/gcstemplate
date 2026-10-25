#ifndef __GCST_UTILS_BASIC_SETTINGS_TPP__
#define __GCST_UTILS_BASIC_SETTINGS_TPP__

#include "gcst/utils/basic_settings.h"

#include <memory>

#include "gcst/utils/ilogger.h"

namespace gcst::utils
{

template <class dsettings>
template <class... Args>
gcst::etype basic_settings <dsettings> ::init(Args&&... args)
{
    auto lparams = std::make_unique <enabler> (std::forward <Args> (args)...);
    if (auto result = lparams->load(); !result)
        return result;
        
    gcst::params = std::move(lparams);
    
    DEBUG("gcst::params have been inited successfully");
    gcst::params->trace();
    return 0;
}

}

#endif