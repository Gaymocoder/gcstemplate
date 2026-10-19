#ifndef __GCST_UTILS_BASIC_LOGGER_H__
#define __GCST_UTILS_BASIC_LOGGER_H__

#include "gcst/utils/ilogger.h"

namespace gcst
{
    namespace utils
    {
        template <class dlogger = void>
        class basic_logger : public ilogger
        {
            using actual = std::conditional_t <std::is_void_v <dlogger>, basic_logger, dlogger>;

            private:
                struct enabler : actual
                {
                    template <class... A>
                    enabler(A&&... a) : actual(std::forward <A> (a)...) {}
                };

            protected:
                using ilogger::ilogger;

            public:
                template <class... Args>
                static gcst::etype init(Args&&... args);

                ~basic_logger() = default;
        };
    }

    using gcst::utils::basic_logger;
}

#include "gcst/utils/basic_logger.tpp"

#endif