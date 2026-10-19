#include "gcst/utils/ilogger.h"

#include <print>
#include <filesystem>

#include <spdlog/cfg/argv.h>
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

std::string_view ilogger::filename()
{
    return this->_filename;
}

ilogger::ilogger(std::string lfilename) : _filename(lfilename) {}

}