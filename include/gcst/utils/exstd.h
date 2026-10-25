#ifndef __GCST_UTILS_EXST__
#define __GCST_UTILS_EXST__

#include <format>
#include <expected>
#include <filesystem>

namespace fs = std::filesystem;

namespace spdlog::level
{
    enum level_enum : int;
    std::string_view format_as(level_enum l);
}


using spdlog::level::level_enum;

template <>
struct std::formatter <level_enum> : public std::formatter <std::string_view>
{
    std::format_context::iterator format(level_enum, std::format_context& ctx) const;
};


namespace gcst
{
    namespace utils
    {
        namespace exstd
        {
            typedef std::expected <int, int> etype;

            fs::path exe_path();
            std::string strnow();

            std::string vstrformat(std::string_view fmt, std::format_args args);

            template <class... Args>
            inline std::string format(std::format_string <Args...> fmt, Args&&... args)
            {
                return vstrformat(fmt.get(), std::make_format_args(args...));
            }

        }

        using namespace gcst::utils::exstd;
    }

    using gcst::utils::etype;
    using gcst::utils::format;
}

#endif