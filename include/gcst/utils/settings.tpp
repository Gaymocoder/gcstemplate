#ifndef __GCST_UTILS_SETTINGS_TPP__
#define __GCST_UTILS_SETTINGS_TPP__

#include "gcst/utils/settings.h"

#include <print>
#include <format>
#include <vector>
#include <fstream>

#include <CLI/CLI.hpp>

#include "gcst/utils/exstd.h"


namespace gcst::utils
{

template <class dsettings>
std::string_view basic_settings <dsettings> ::get(std::string key)
{
    return this->dict.at(key);
}
    
template <class dsettings>
void basic_settings <dsettings> ::set(std::string key, std::string value)
{
    this->dict[key] = value;
}

template <class dsettings>
void basic_settings <dsettings> ::write()
{
    std::ofstream fconf = std::ofstream(this->config_path);
    for(const auto& [key, value] : this->dict)
        if (key != "override-config")
            fconf << std::format("{}=\'{}\'\n", key, value);
}

template <class dsettings>
void basic_settings <dsettings> ::set_to_defaults()
{
    fs::path log_dir = this->mydir/"logs";
    this->set("logdir-path", log_dir.string());
    
    this->set("file-loglevel", "info");
    this->set("console-loglevel", "info");

    this->set("override-config", "false");
}

template <class dsettings>
void basic_settings <dsettings> ::reset_to_defaults()
{
    this->set_to_defaults();
    this->write();
}

template <class dsettings>
gcst::etype basic_settings <dsettings> ::extract()
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

template <class dsettings>
const std::map <std::string, std::string>& basic_settings <dsettings> ::list()
{
    return this->dict;
}

template <class dsettings>
basic_settings <dsettings> ::basic_settings (int largc, char** largv, std::shared_ptr <CLI::App> lcli)
    : argc(largc), argv(largv), cli(lcli)
{
    if (!(this->cli)) {
        this->cli = std::make_shared <CLI::App> ("GCS.Template");
    }
    this->cli->allow_non_standard_option_names();
}

template <class dsettings>
template <class... Args>
gcst::etype basic_settings <dsettings> ::init(Args&&... args)
{
    params = std::make_unique <enabler> (std::forward <Args> (args)...);
    
    params->set_to_defaults();
    if (!fs::exists(params->config_path))
        params->write();
    
    if (!(params->extract()))
        return std::unexpected(1);

    if (params->get("override-config") == "true")
        params->write();

    return 0;
}

}

#endif