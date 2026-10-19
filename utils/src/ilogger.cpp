#include "gcst/utils/ilogger.h"

#include <print>
#include <filesystem>

#include <spdlog/spdlog.h>
#include <spdlog/pattern_formatter.h>
#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/sinks/stdout_color_sinks.h>

#include "gcst/utils/exstd.h"
#include "gcst/utils/settings.h"

namespace fs = std::filesystem;

const char* logger_name = "gcstemplate";

namespace gcst::utils
{

class file_ptr_flag : public spdlog::custom_flag_formatter
{
    public:
        void format(const spdlog::details::log_msg &msg, const std::tm &, spdlog::memory_buf_t &dest) override
        {
            std::string filename = fs::path(msg.source.filename).filename().string();
            std::string new_flag = std::format("{}:{}", filename, msg.source.line);

            std::string paddered;
            typedef spdlog::details::padding_info::pad_side padside;

            if (padinfo_.truncate_ && new_flag.length() > padinfo_.width_)
                new_flag = new_flag.substr(0, padinfo_.width_);
            
            switch (padinfo_.side_)
            {
                case padside::left:
                    paddered = std::format("{:>{}}", new_flag, padinfo_.width_);
                    break;

                case padside::center:
                    paddered = std::format("{:^{}}", new_flag, padinfo_.width_);
                    break;

                case padside::right:
                    paddered = std::format("{:<{}}", new_flag, padinfo_.width_);
                    break;
            }
            
            dest.append(paddered.data(), paddered.data() + paddered.size());
        }

        std::unique_ptr <custom_flag_formatter> clone() const override
        {
            return spdlog::details::make_unique<file_ptr_flag>();
        }
};

const fs::path& ilogger::filepath() const
{
    return this->_filepath;
}

gcst::etype ilogger::formatter_init()
{
    auto formatter = std::make_unique <spdlog::pattern_formatter> ();
    
    formatter->add_flag <file_ptr_flag> ('K');
    formatter->set_pattern("[%d.%m.%Y %T.%f]  %^%-8l%$  %-15K %v");

    if (!this->logger)
        return std::unexpected(1);

    this->logger->set_formatter(std::move(formatter));
    return 0;
}

std::expected <ilogger::spdsink_ptr, int> ilogger::file_sink_init()
{
    if (!GCST_SETTINGS_INITED)
        return std::unexpected(1);
    
    auto file_loglevel = gcst::params->get("file-loglevel");
    auto file_sink = std::make_shared <spdlog::sinks::basic_file_sink_mt> (this->filepath().string(), false);
    file_sink->set_level(spdlog::level::from_str(std::string(*file_loglevel)));
    return file_sink;
}

std::expected <ilogger::spdsink_ptr, int> ilogger::console_sink_init()
{
    if (!GCST_SETTINGS_INITED)
        return std::unexpected(1);
    
    auto console_loglevel = gcst::params->get("console-loglevel");
    auto console_sink = std::make_shared <spdlog::sinks::stderr_color_sink_mt> ();
    console_sink->set_level(spdlog::level::from_str(std::string(*console_loglevel)));

    return console_sink;
}

gcst::etype ilogger::setup()
{
    auto file_sink = this->file_sink_init();
    auto console_sink = this->console_sink_init();

    if (!(file_sink && console_sink))
        return std::unexpected(1);

    this->logger = std::make_shared <spdlog::logger> (logger_name, spdlog::sinks_init_list {*file_sink, *console_sink});
    this->logger->set_level(spdlog::level::trace);
    this->logger->flush_on(spdlog::level::trace);
    
    if (auto result = this->formatter_init(); !result)
        return std::unexpected(2);

    spdlog::set_default_logger(this->logger);
    return 0;
}

ilogger::ilogger(const fs::path& dir, std::string filename)
{
    this->_filepath = dir/filename;
}

ilogger::~ilogger() {}

}