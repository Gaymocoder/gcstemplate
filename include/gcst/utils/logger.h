#ifndef __GCST_UTILS_LOGGER_H__
#define __GCST_UTILS_LOGGER_H__

#include "gcst/utils/basic_logger.h"

namespace gcst
{
    namespace utils
    {
        typedef basic_logger <> logger;
    }

    using gcst::utils::logger;
}

#endif