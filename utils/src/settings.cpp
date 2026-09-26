#include "gcst/utils/settings.h"
#include "gcst/utils/exstd.h"

#include <initializer_list>

namespace gcst::utils
{

void settings::set_to_defaults()
{
    settings::logdir_path = mydir/"logs";
    
    settings::file_loglevel = "INFO";
    settings::console_loglevel = "INFO";
}

}