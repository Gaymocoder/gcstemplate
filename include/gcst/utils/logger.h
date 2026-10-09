#ifndef __GCST_UTILS_LOGGER_H__
#define __GCST_UTILS_LOGGER_H__

#include <string>

#include <spdlog/spdlog.h>

#define GCST_SPDLOG_INITED gcst::utils::spdlog::inited()

#define TRACE     if(GCST_SPDLOG_INITED) SPDLOG_TRACE
#define DEBUG     if(GCST_SPDLOG_INITED) SPDLOG_DEBUG
#define INFO      if(GCST_SPDLOG_INITED) SPDLOG_INFO
#define WARN      if(GCST_SPDLOG_INITED) SPDLOG_WARN
#define ERROR     if(GCST_SPDLOG_INITED) SPDLOG_ERROR
#define CRITICAL  if(GCST_SPDLOG_INITED) SPDLOG_CRITICAL

namespace gcst::utils
{
    class logger
    {
        private:
            logger();
            bool _inited;

        public:
            static void init();

            const bool& inited();
    }

    std::unique_ptr <gcst::utils::log> journal;
}

#endif