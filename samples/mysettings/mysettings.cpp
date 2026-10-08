#include "mysettings.h"

#include <CLI/CLI.hpp>

using gcst::settings;

void mysettings::set_to_defaults()
{
    // Import gcst settings, if it's needed
    isettings::set_to_defaults();

    // Add some of your own
    /// Ordinary default setting for custom cli parsing in future
    this->set("level", "medium");

    /// Adds option or flag to cli-object automatically
    this->set("port", "8080", settings::type::option);
}

gcst::etype mysettings::extract()
{
    // Custom option add into CLI-object
    this->cli->add_option("--level", this->dict["level"])
        ->check(CLI::IsMember({"low", "medium", "high"}, CLI::ignore_case));

    // Parsing gcst settings, if it's needed
    return isettings::extract();

    /*
      * Without parsing basic gcst settings you should parse your own maunally
      *
      * this->cli->set_config("--config", this->config_path.string());
      * try {
      *     this->cli->parse(this->argc, this->argv);
      * } catch (CLI::ParseError &e) {
      *     return std::unexpected(this->cli->exit(e));
      * }
    */
}