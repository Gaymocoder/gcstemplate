#include "gcst/utils/settings.h"

#include <print>
#include <format>
#include <vector>
#include <fstream>

#include <CLI/CLI.hpp>

#include "gcst/utils/exstd.h"


namespace gcst::utils
{

std::string_view settings::get(std::string key)
{
    return settings::dict.at(key);
}
    
void settings::set(std::string key, std::string value)
{
    settings::dict[key] = value;
}

void settings::write()
{
    std::ofstream fconf = std::ofstream(settings::config_path);
    for(const auto& [key, value] : settings::dict)
        if (key != "override-config")
            fconf << std::format("{}=\'{}\'\n", key, value);
}

void settings::set_to_defaults()
{
    fs::path log_dir = settings::mydir/"logs";
    settings::set("logdir-path", log_dir.string());
    
    settings::set("file-loglevel", "info");
    settings::set("console-loglevel", "info");

    settings::set("override-config", "false");
}

void settings::reset_to_defaults()
{
    settings::set_to_defaults();
    settings::write();
}

gcst::etype settings::extract(CLI::App& app)
{
    const std::vector <std::string> loglevels {
        "trace", "debug", "info", "warn", "error", "critical"
    };

    app.add_flag("-oc, --override-config", settings::dict["override-config"]);
    app.add_option("-ldp,--logdir-path", settings::dict["logdir-path"]);
    app.add_option("-fll,--file-loglevel", settings::dict["file-loglevel"])
        ->check(CLI::IsMember(loglevels, CLI::ignore_case));
    app.add_option("-cll,--console-loglevel", settings::dict["console-loglevel"])
        ->check(CLI::IsMember(loglevels, CLI::ignore_case));
    
    app.set_config("--config", settings::config_path.string());
    try {
        app.parse(settings::argc, settings::argv);
    } catch (CLI::ParseError &e) {
        return std::unexpected(app.exit(e));
    }

    fs::create_directories(settings::dict["logdir-path"]);
    return 0;
}

const std::map <std::string, std::string>& settings::list()
{
    return dict;
}

gcst::etype settings::init(int largc, char** largv)
{
    settings::argc = largc;
    settings::argv = largv;

    CLI::App app{"GCS.Template"};
    app.allow_non_standard_option_names();

    settings::set_to_defaults();
    if (!fs::exists(settings::config_path))
        settings::write();
    
    if (!settings::extract(app))
        return std::unexpected(1);

    if (settings::get("override-config") == "true")
        settings::write();

    return 0;
}

}