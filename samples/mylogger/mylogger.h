#ifndef __GCST_SAMPLES_MYLOGGER_H__
#define __GCST_SAMPLES_MYLOGGER_H__

#include <gcst/gcst.h>
#include <spdlog/common.h>

class mylogger : public gcst::basic_logger <mylogger>
{
    protected:
        using basic_logger::basic_logger;

        // Kept to give the console its own pattern in formatter_init()
        spdlog::sink_ptr console;

        gcst::etype formatter_init() override;
        std::expected <spdlog::sink_ptr, int> file_sink_init() override;
        std::expected <spdlog::sink_ptr, int> console_sink_init() override;
};

#endif
