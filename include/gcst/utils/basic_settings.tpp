#ifndef __GCST_UTILS_BASIC_SETTINGS_TPP__
#define __GCST_UTILS_BASIC_SETTINGS_TPP__

#include "gcst/utils/settings.h"

#include <memory>

namespace gcst::utils
{

template <class dsettings>
template <class... Args>
gcst::etype basic_settings <dsettings> ::init(Args&&... args)
{
    auto lparams = std::make_unique <enabler> (std::forward <Args> (args)...);
    if (auto result = lparams->load(); !result)
        return result;

    params = std::move(lparams);
    return 0;
}

}

#endif