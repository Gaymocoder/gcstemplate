cmake_minimum_required(VERSION 3.31)
project(gcstemplate_utils)

find_package(CLI11 REQUIRED)

set(gcst_exstd_lib src/exstd.cpp)
set(gcst_isettings_lib src/isettings.cpp)

add_library(gcst_utils_exstd OBJECT ${gcst_exstd_lib})
add_library(gcst_utils_isettings OBJECT ${gcst_isettings_lib})

list(APPEND gcst_utils_objs gcst_utils_exstd)
list(APPEND gcst_utils_objs gcst_utils_isettings)

target_link_libraries(gcst_utils_isettings PRIVATE CLI11::CLI11)

gcst_binary_prepare(gcst_utils_exstd)
gcst_binary_prepare(gcst_utils_isettings)

add_library(gcst_utils STATIC)
target_link_libraries(gcst_utils PUBLIC CLI11::CLI11)
gcst_export_prepare(gcst_utils ${gcst_utils_objs})