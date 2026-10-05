cmake_minimum_required(VERSION 3.31)
project(gcstemplate_utils)

set(gcst_exstd_lib src/exstd.cpp)
set(gcst_settings_lib src/settings.cpp)

add_library(gcst_utils_exstd OBJECT ${gcst_exstd_lib})
add_library(gcst_utils_settings OBJECT ${gcst_settings_lib})

list(APPEND gcst_utils_objs gcst_utils_exstd)
list(APPEND gcst_utils_objs gcst_utils_settings)

target_link_libraries(gcst_utils_settings PRIVATE CLI11::CLI11)

gcst_binary_prepare(gcst_utils_exstd)
gcst_binary_prepare(gcst_utils_settings)

add_library(gcst_utils STATIC)
gcst_export_prepare(gcst_utils ${gcst_utils_objs})