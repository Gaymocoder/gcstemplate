cmake_minimum_required(VERSION 3.31)
project(GCST_Hello)

set(MAIN_EXE src/main.cpp)
add_executable(gcst_hello_exe ${MAIN_EXE})

target_link_libraries(gcst_hello_exe PRIVATE Boost::headers)
set_target_properties(gcst_hello_exe PROPERTIES OUTPUT_NAME "GCST.Hello")

gcst_binary_prepare(gcst_hello_exe)