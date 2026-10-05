#ifndef __GCST_UTILS_SETTINGS_H__
#define __GCST_UTILS_SETTINGS_H__

#include "gcst/utils/exstd.h"

#include <map>
#include <tuple>
#include <string>
#include <filesystem>

namespace fs = std::filesystem;
namespace CLI {class App;}

namespace gcst::utils
{
    class settings
    {
        private:
            settings();

        protected:
            inline static int argc;
            inline static char** argv;

            inline static fs::path mydir = exstd::exe_path().parent_path();
            inline static fs::path config_path = mydir/"settings.conf";
            inline static std::map <std::string, std::string> dict;

            static gcst::etype extract(CLI::App&);

        public:
            static gcst::etype init(int, char**);

            static void write();
            
            static void set_to_defaults();
            static void reset_to_defaults();

            static void set(std::string, std::string);
            static std::string_view get(std::string);

            static const std::map <std::string, std::string>& list();
    };
}

#endif