#include "gcst/utils/isettings.h"

#include <vector>
#include <fstream>

#include <CLI/CLI.hpp>

#include "gcst/utils/exstd.h"
#include "gcst/utils/logger.h"

namespace gcst::utils 
{

std::expected <std::string_view, int> isettings::get(std::string key)
{
    if (auto it = dict.find(key); it != dict.end())
    {
        if (it->second != "")
            return it->second;
        return std::unexpected(1);
    }
    return std::unexpected(2);
}
    
void isettings::set(std::string key, std::string value)
{
    this->dict[key] = value;
    DEBUG("Param '{}' was set to '{}'", key, value);
}

void isettings::set(std::string key, std::string value, isettings::type settype)
{
    this->set(key, value);
    std::string settype_str = "";
    switch (settype)
    {
        case isettings::type::flag:
            this->cli->add_flag(gcst::format("--{}", key), this->dict[key]);
            settype_str = "flag";
            break;

        case isettings::type::option:
            this->cli->add_option(gcst::format("--{}", key), this->dict[key]);
            settype_str = "option";
            break;
    }
    TRACE("Param '{}' was added to CLI11::App as {}", key, settype_str);
}

void isettings::write()
{
    using DictIter = std::map <std::string, std::string> ::iterator;
    std::vector <DictIter> written_params;
    written_params.reserve(this->dict.size());

    std::ofstream fconf = std::ofstream(this->config_path);
    DEBUG("Writing down params into {}", this->config_relpath().string());
    for(const auto& [key, value] : this->dict)
    {
        if (key != "override-config" && key != "logfile-name")
        {
            fconf << gcst::format("{}=\'{}\'\n", key, value);
            TRACE("/tparam saved -> '{}': '{}'", key, value);
        }
    }
}

void isettings::set_to_defaults()
{
    fs::path log_dir = this->mydir/"logs";
    std::string logfile_name = gcst::utils::strnow() + ".gcstlog";

    DEBUG("Setting params to their defaults");
    this->set("logdir-path", log_dir.string());
    this->set("logfile-name", logfile_name);
    this->set("file-loglevel", "info");
    this->set("console-loglevel", "info");
    this->set("override-config", "false");
}

void isettings::reset_to_defaults()
{
    this->set_to_defaults();
    this->write();
}

gcst::etype isettings::parse()
{
    DEBUG("Parsing params from config-file ({})", this->config_relpath().string());
    this->cli->set_config("--config", this->config_path.string());

    DEBUG("Overriding params from CLI");
    try 
    {
        this->cli->parse(this->argc, this->argv);
    }
    catch (CLI::ParseError &e)
    {
        return std::unexpected(this->cli->exit(e));
    }

    return 0;
}

gcst::etype isettings::extract()
{
    const std::vector <std::string> loglevels {
        "trace", "debug", "info", "warn", "error", "critical"
    };

    this->cli->add_flag("-oc, --override-config", this->dict["override-config"]);
    this->cli->add_option("-ldp,--logdir-path", this->dict["logdir-path"]);
    this->cli->add_option("-lfn,--logfile-name", this->dict["logfile-name"]);
    this->cli->add_option("-fll,--file-loglevel", this->dict["file-loglevel"])
        ->check(CLI::IsMember(loglevels, CLI::ignore_case));
    this->cli->add_option("-cll,--console-loglevel", this->dict["console-loglevel"])
        ->check(CLI::IsMember(loglevels, CLI::ignore_case));
    
    if (auto result = this->parse(); !result)
    {
        ERROR("Failed to parse arguments from CLI with error code {}", result.error());
        return std::unexpected(1);
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

fs::path isettings::config_relpath()
{
    return fs::path(".")/fs::relative(this->config_path, gcst::utils::exe_path().parent_path());
}

void isettings::log(gcst::loglevel lvl, std::source_location sl)
{
    for(const auto& [key, value] : this->dict)
        GCST_LOG_FROM(lvl, sl, "  Option {:<25}{}", gcst::format("'{}':", key), value);
}

isettings::isettings (int largc, char** largv, std::shared_ptr <CLI::App> lcli)
    : argc(largc), argv(largv), cli(lcli), mydir(exstd::exe_path().parent_path()), config_path(mydir/"settings.conf")
{
    if (!(this->cli)) {
        this->cli = std::make_shared <CLI::App> ("GCS.Template");
        TRACE("CLI::App initialized");
    }
    this->cli->allow_non_standard_option_names();
}

isettings::~isettings () = default;

}