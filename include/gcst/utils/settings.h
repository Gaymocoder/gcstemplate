#include <string>
#include <filesystem>

namespace fs = std::filesystem;

namespace gcst::utils
{
    class settings
    {
        private:
            settings();
            inline static fs::path logdir_path;
            inline static fs::path config_path = "settings.conf";

            inline static std::string file_loglevel;
            inline static std::string console_loglevel;

        public:
            static void init();
            static void set_to_defaults();
            static void reset_to_defaults();
            static void read_from_cli();
            static void read_from_config();

    };
}