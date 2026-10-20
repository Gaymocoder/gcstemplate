#include "mylogger.h"

#include <spdlog/sinks/rotating_file_sink.h>

std::expected <spdlog::sink_ptr, int> mylogger::file_sink_init()
{
    // Replace gcst file sink with a rotating one: up to 3 files by 1 MiB
    auto file_loglevel = gcst::params->get("file-loglevel");
    if (!file_loglevel)
        return std::unexpected(file_loglevel.error());

    auto file_sink = std::make_shared <spdlog::sinks::rotating_file_sink_mt> (this->filepath().string(), 1024 * 1024, 3);
    file_sink->set_level(spdlog::level::from_str(std::string(*file_loglevel)));
    return file_sink;

    /*
      * Use gcst file sink, if it's enough
      *
      * return ilogger::file_sink_init();
    */
}

std::expected <spdlog::sink_ptr, int> mylogger::console_sink_init()
{
    // Import gcst console sink, it's already leveled by "--console-loglevel"
    auto console_sink = ilogger::console_sink_init();

    // And remember it to format separately from the file
    if (console_sink)
        this->console = *console_sink;

    return console_sink;
}

gcst::etype mylogger::formatter_init()
{
    // ilogger::setup() calls it after both sinks are created.
    // gcst formatter sets its detailed pattern to every sink of the logger
    if (auto result = ilogger::formatter_init(); !result)
        return result;

    // So the console pattern goes after it, the file keeps the detailed one
    this->console->set_pattern("%^%-8l%$ %v");
    return 0;
}
