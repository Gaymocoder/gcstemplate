#include "gcst/utils/exstd.h"

#ifdef _WIN32
    #include <windows.h>
#endif

#include <string>

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

}