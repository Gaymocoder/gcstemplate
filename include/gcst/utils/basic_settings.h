#ifndef __GCST_UTILS_BASIC_SETTINGS_H__
#define __GCST_UTILS_BASIC_SETTINGS_H__

#include "gcst/utils/exstd.h"
#include "gcst/utils/isettings.h"

namespace CLI {class App;}

namespace gcst::utils
{
    template <class dsettings = void>
    class basic_settings : public isettings
    {
        using actual = std::conditional_t <std::is_void_v <dsettings>, basic_settings, dsettings>;
        
        private:
            struct enabler : actual
            {
                template <class... A>
                enabler(A&&... a) : actual(std::forward <A> (a)...) {}
            };
        
        protected:
            using isettings::isettings;
        
        public:
            template <class... Args>
            static gcst::etype init(Args&&... args);

            ~basic_settings() = default;
    };
}

#include "gcst/utils/basic_settings.tpp"

#endif