cmake_minimum_required(VERSION 3.31)
project(gcstemplate_sample_basic_settings)

block()
    set(main_exe main.cpp)

    add_executable(gcst_sample_basic_settings ${main_exe})

    target_link_libraries(gcst_sample_basic_settings PRIVATE gcst::utils)

    gcst_binary_prepare(gcst_sample_basic_settings)

    set_target_properties(gcst_sample_basic_settings PROPERTIES OUTPUT_NAME "samples.BasicSettings")
endblock()