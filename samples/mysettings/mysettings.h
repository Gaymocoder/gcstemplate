#include <gcst/gcst.h>

class mysettings : public gcst::basic_settings <mysettings>
{
    protected:
        using basic_settings::basic_settings;

    public:
        void set_to_defaults() override;
        gcst::etype extract() override;
};
