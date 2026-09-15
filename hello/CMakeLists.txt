cmake_minimum_required(VERSION 3.31)
project(GCST_Hello)

set(gcst_showcase_lib src/showcase.cpp)
set(MAIN_EXE src/main.cpp)

add_library(gcst_hello_showcase OBJECT ${gcst_showcase_lib})
add_executable(gcst_hello_exe ${MAIN_EXE})

target_link_libraries(gcst_hello_showcase PRIVATE gcst::utils)
target_link_libraries(gcst_hello_showcase PRIVATE Boost::headers)

target_link_libraries(gcst_hello_exe PRIVATE gcst_hello_showcase)

gcst_binary_prepare(gcst_hello_showcase)
gcst_binary_prepare(gcst_hello_exe)

set_target_properties(gcst_hello_exe PROPERTIES OUTPUT_NAME "GCST.Hello")
