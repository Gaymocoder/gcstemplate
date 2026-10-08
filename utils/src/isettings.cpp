#include "gcst/utils/isettings.h"

#include <vector>
#include <format>
#include <fstream>

#include <CLI/CLI.hpp>

namespace gcst::utils 
{

std::string_view isettings::get(std::string key)
{
    return this->dict.at(key);
}
    
void isettings::set(std::string key, std::string value)
{
    this->dict[key] = value;
}

void isettings::write()
{
    std::ofstream fconf = std::ofstream(this->config_path);
    for(const auto& [key, value] : this->dict)
        if (key != "override-config")
            fconf << std::format("{}=\'{}\'\n", key, value);
}

void isettings::set_to_defaults()
{
    fs::path log_dir = this->mydir/"logs";
    this->set("logdir-path", log_dir.string());
    
    this->set("file-loglevel", "info");
    this->set("console-loglevel", "info");

    this->set("override-config", "false");
}

void isettings::reset_to_defaults()
{
    this->set_to_defaults();
    this->write();
}

gcst::etype isettings::extract()
{
    const std::vector <std::string> loglevels {
        "trace", "debug", "info", "warn", "error", "critical"
    };

    this->cli->add_flag("-oc, --override-config", this->dict["override-config"]);
    this->cli->add_option("-ldp,--logdir-path", this->dict["logdir-path"]);
    this->cli->add_option("-fll,--file-loglevel", this->dict["file-loglevel"])
        ->check(CLI::IsMember(loglevels, CLI::ignore_case));
    this->cli->add_option("-cll,--console-loglevel", this->dict["console-loglevel"])
        ->check(CLI::IsMember(loglevels, CLI::ignore_case));
    
    this->cli->set_config("--config", this->config_path.string());
    try {
        this->cli->parse(this->argc, this->argv);
    } catch (CLI::ParseError &e) {
        return std::unexpected(this->cli->exit(e));
    }

    fs::create_directories(this->dict["logdir-path"]);
    return 0;
}

gcst::etype isettings::load()
{
    this->set_to_defaults();
    if (!fs::exists(this->config_path))
        this->write();

    if (!(this->extract()))
        return std::unexpected(1);

    if (this->get("override-config") == "true")
        this->write();

    return 0;
}

const std::map <std::string, std::string>& isettings::list()
{
    return this->dict;
}

isettings::isettings (int largc, char** largv, std::shared_ptr <CLI::App> lcli)
    : argc(largc), argv(largv), cli(lcli), mydir(exstd::exe_path().parent_path()), config_path(mydir/"settings.conf")
{
    if (!(this->cli)) {
        this->cli = std::make_shared <CLI::App> ("GCS.Template");
    }
    this->cli->allow_non_standard_option_names();
}

isettings::~isettings () = default;

}