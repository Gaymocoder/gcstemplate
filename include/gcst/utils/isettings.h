#ifndef __GCST_UTILS_ISETTINGS_H__
#define __GCST_UTILS_ISETTINGS_H__

#include <map>
#include <memory>
#include <expected>
#include <source_location>

#include "gcst/utils/exstd.h"

#define GCST_SETTINGS_INITED (gcst::utils::params)

namespace CLI { class App; }

namespace gcst
{
    namespace utils
    {
        class isettings
        {
            private:
                int argc;
                char** argv;

            protected:
                isettings(int argc, char** argv, std::shared_ptr <CLI::App> lcli = nullptr);

                std::shared_ptr <CLI::App> cli;
                std::map <std::string, std::string> dict;

                fs::path mydir;
                fs::path config_path;

                virtual etype parse() final;

                virtual etype load();
                virtual etype extract();

            public:
                enum class type {
                    flag,
                    option,
                };

                virtual void write();
                virtual void set_to_defaults();
                virtual void reset_to_defaults();

                virtual void set(std::string, std::string);
                virtual void set(std::string, std::string, type settype);
                virtual std::expected <std::string_view, int> get(std::string);

                const std::map <std::string, std::string>& list();
                virtual fs::path config_relpath() final;

                virtual void log(gcst::loglevel, std::source_location sl = std::source_location::current());
                virtual ~isettings() = 0;
        };

        inline std::unique_ptr <isettings> params = nullptr;
    }

    using gcst::utils::params;
}

#endif