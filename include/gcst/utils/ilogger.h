#ifndef __GCST_UTILS_ILOGGER_H__
#define __GCST_UTILS_ILOGGER_H__

#include <mutex>
#include <string>
#include <filesystem>

#include <spdlog/fwd.h>

#include "gcst/utils/exstd.h"

namespace fs = std::filesystem;

#define GCST_LOGGER_INITED (gcst::utils::journal)

#define TRACE     if(GCST_LOGGER_INITED) SPDLOG_TRACE
#define DEBUG     if(GCST_LOGGER_INITED) SPDLOG_DEBUG
#define INFO      if(GCST_LOGGER_INITED) SPDLOG_INFO
#define WARN      if(GCST_LOGGER_INITED) SPDLOG_WARN
#define ERROR     if(GCST_LOGGER_INITED) SPDLOG_ERROR
#define CRITICAL  if(GCST_LOGGER_INITED) SPDLOG_CRITICAL

namespace gcst
{
    namespace utils
    {
        class ilogger
        {
            using spdsink_ptr = std::shared_ptr <spdlog::sinks::sink>;

            protected:
                ilogger(const fs::path&, std::string);

                fs::path _filepath;
                
                virtual gcst::etype setup();
                
                virtual gcst::etype formatter_init();
                virtual std::expected <spdsink_ptr, int> file_sink_init();
                virtual std::expected <spdsink_ptr, int> console_sink_init();
                
            public:
                const fs::path& filepath() const;
                
                std::shared_ptr <spdlog::logger> logger;
                virtual ~ilogger() = 0;
        };

        inline std::unique_ptr <ilogger> journal = nullptr;
    }

    using gcst::utils::journal;
}
#endif