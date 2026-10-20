cmake_minimum_required(VERSION 3.31)
project(gcstemplate_sample_mylogger)

block()
    set(mylogger_lib mylogger.cpp)
    set(main_exe main.cpp)

    add_library(mylogger OBJECT ${mylogger_lib})
    add_executable(gcst_sample_mylogger ${main_exe})

    target_link_libraries(mylogger PUBLIC gcst::utils)
    target_link_libraries(gcst_sample_mylogger PRIVATE mylogger)

    gcst_binary_prepare(mylogger)
    gcst_binary_prepare(gcst_sample_mylogger)

    set_target_properties(gcst_sample_mylogger PROPERTIES OUTPUT_NAME "samples.Mylogger")
endblock()