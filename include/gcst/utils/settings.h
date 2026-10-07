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
    template <class dsettings = void>
    class basic_settings
    {
        using actual = std::conditional_t <std::is_void_v <dsettings>, basic_settings, dsettings>;
        
        private:
            int argc;
            char** argv;

            struct enabler : actual
            {
                template <class... A>
                enabler(A&&... a) : actual(std::forward <A> (a)...) {}
            };
        
        protected:
            basic_settings(int largc, char** largv, std::shared_ptr <CLI::App> lcli = nullptr);
            
            std::shared_ptr <CLI::App> cli;
            std::map <std::string, std::string> dict;
            
            fs::path mydir = exstd::exe_path().parent_path();
            fs::path config_path = mydir/"settings.conf";
            
            virtual gcst::etype extract();
        
        public:
            template <class... Args>
            static gcst::etype init(Args&&... args);
            
            virtual void write();
            virtual void set_to_defaults();
            virtual void reset_to_defaults();
            
            virtual std::string_view get(std::string);
            virtual void set(std::string, std::string);
            
            const std::map <std::string, std::string>& list();

            virtual ~basic_settings() = default;
    };

    typedef basic_settings <> settings;
    inline std::unique_ptr <settings> params;
}

#include "gcst/utils/settings.tpp"

#endif