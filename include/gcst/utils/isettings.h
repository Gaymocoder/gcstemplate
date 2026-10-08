#ifndef __GCST_UTILS_ISETTINGS_H__
#define __GCST_UTILS_ISETTINGS_H__

#include <map>
#include <memory>

#include "gcst/utils/exstd.h"

namespace CLI { class App; }

namespace gcst::utils
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

            void set(std::string, std::string);
            void set(std::string, std::string, type settype);
            std::string_view get(std::string);

            const std::map <std::string, std::string>& list();

            virtual ~isettings() = 0;
    };

    inline std::unique_ptr <isettings> params;
}

#endif