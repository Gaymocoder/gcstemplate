cmake_minimum_required(VERSION 3.31)
project(gcstemplate_sample_mysettings)

block()
    set(mysettings_lib mysettings.cpp)
    set(main_exe main.cpp)

    add_library(mysettings OBJECT ${mysettings_lib})
    add_executable(gcst_sample_mysettings ${main_exe})

    target_link_libraries(mysettings PRIVATE gcst::utils)
    target_link_libraries(gcst_sample_mysettings PRIVATE mysettings)

    gcst_binary_prepare(mysettings)
    gcst_binary_prepare(gcst_sample_mysettings)

    set_target_properties(gcst_sample_mysettings PROPERTIES OUTPUT_NAME "samples.Mysettings")
endblock()