#ifndef __GCST_UTILS_LOGGER_H__
#define __GCST_UTILS_LOGGER_H__

#include <string>

#include <spdlog/spdlog.h>

#include "gcst/utils/exstd.h"

#define GCST_SPDLOG_INITED (gcst::utils::journal)

#define TRACE     if(GCST_SPDLOG_INITED) SPDLOG_TRACE
#define DEBUG     if(GCST_SPDLOG_INITED) SPDLOG_DEBUG
#define INFO      if(GCST_SPDLOG_INITED) SPDLOG_INFO
#define WARN      if(GCST_SPDLOG_INITED) SPDLOG_WARN
#define ERROR     if(GCST_SPDLOG_INITED) SPDLOG_ERROR
#define CRITICAL  if(GCST_SPDLOG_INITED) SPDLOG_CRITICAL

namespace gcst
{
    namespace utils
    {
        class ilogger
        {
            protected:
                ilogger(std::string);
                std::string _filename;

            public:
                std::string_view filename();
        };

        inline std::unique_ptr <ilogger> journal = nullptr;
    }

    using gcst::utils::journal;
}
#endif