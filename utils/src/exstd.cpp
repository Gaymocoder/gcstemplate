#include "gcst/utils/exstd.h"

#include <string>
#include <chrono>
#include <format>

#ifdef _WIN32
    #include <windows.h>
#endif

#include <spdlog/common.h>

std::format_context::iterator std::formatter <level_enum> ::format(level_enum lvl, std::format_context& ctx) const
{
    auto svt = to_string_view(lvl);
    std::string_view sv {svt.data(), svt.size()};
    return std::formatter <std::string_view> ::format(sv, ctx);
}

namespace spdlog::level 
{

std::string_view format_as(level_enum lvl)
{
    auto sv = to_string_view(lvl);
    return {sv.data(), sv.size()};
}

}

namespace gcst::utils::exstd
{

#ifdef _WIN32

fs::path exe_path()
{
    std::wstring wstrpath(MAX_PATH, L'\0');
    while (true)
    {
        DWORD total_wchars = GetModuleFileNameW(nullptr, wstrpath.data(), MAX_PATH);
        if (total_wchars == 0)
            return {};

        if (total_wchars < wstrpath.size())
        {
            wstrpath.resize(total_wchars);
            break;
        }
        wstrpath.resize(wstrpath.size() * 2);
    }

    return fs::path(wstrpath);
}

#else

fs::path exe_path()
{
    return fs::read_symlink("/proc/self/exe");
}

#endif

std::string strnow()
{
    auto now = std::chrono::floor <std::chrono::seconds> (std::chrono::system_clock::now());
    return std::format("{0:%F_%H-%M-%S}", now);
}

}