#ifndef __GCST_UTILS_ILOGGER_H__
#define __GCST_UTILS_ILOGGER_H__

#include <string>
#include <filesystem>
#include <source_location>

#include <spdlog/fwd.h>

#include "gcst/utils/exstd.h"

namespace fs = std::filesystem;

#define GCST_LOGGER_INITED (gcst::utils::journal)

#define GCST_LOG(lvl, ...) \
    do \
    { \
        if (gcst::utils::ilogger::is_active(lvl)) \
            gcst::utils::ilogger::write(lvl, std::source_location::current(), gcst::format(__VA_ARGS__)); \
    } while (0)

#define GCST_LOG_FROM(lvl, sl, ...) \
    do \
    { \
        if (gcst::utils::ilogger::is_active(lvl)) \
            gcst::utils::ilogger::write(lvl, sl, gcst::format(__VA_ARGS__)); \
    } while (0)

#define TRACE(...)     GCST_LOG(gcst::utils::loglevel::trace, __VA_ARGS__);
#define DEBUG(...)     GCST_LOG(gcst::utils::loglevel::debug, __VA_ARGS__);
#define INFO(...)      GCST_LOG(gcst::utils::loglevel::info, __VA_ARGS__);
#define WARN(...)      GCST_LOG(gcst::utils::loglevel::warn, __VA_ARGS__);
#define ERROR(...)     GCST_LOG(gcst::utils::loglevel::error, __VA_ARGS__);
#define CRITICAL(...)  GCST_LOG(gcst::utils::loglevel::critical, __VA_ARGS__);

namespace gcst
{
    namespace utils
    {
        enum class loglevel : int 
        {
            trace,
            debug,
            info,
            warn,
            error,
            critical,
        };

        class ilogger
        {
            using spdsink_ptr = std::shared_ptr <spdlog::sinks::sink>;
            
            protected:
                ilogger(const fs::path&, std::string);
                
                fs::path _filepath;
                std::shared_ptr <spdlog::logger> _logger;
                std::shared_ptr <spdlog::sinks::sink> _filesink;
                std::shared_ptr <spdlog::sinks::sink> _consolesink;
                
                virtual gcst::etype setup();
                virtual gcst::etype formatter_init();
                virtual std::expected <spdsink_ptr, int> file_sink_init();
                virtual std::expected <spdsink_ptr, int> console_sink_init();
                
            public:
                const fs::path& filepath() const;
                fs::path relfilepath() const;
                
                const std::shared_ptr <spdlog::logger> logger() const {return _logger;}
                const std::shared_ptr <spdlog::sinks::sink> filesink() const {return _filesink;}
                const std::shared_ptr <spdlog::sinks::sink> consolesink() const {return _consolesink;}

                static bool is_active(loglevel);
                static void write(loglevel, std::source_location, std::string);

                virtual ~ilogger() = 0;
        };

        inline std::unique_ptr <ilogger> journal = nullptr;
    }

    using gcst::utils::journal;
}
#endif