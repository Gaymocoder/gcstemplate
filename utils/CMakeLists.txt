cmake_minimum_required(VERSION 3.31)
project(gcstemplate_utils)

set(gcst_exstd_lib src/exstd.cpp)
add_library(gcst_utils_exstd OBJECT ${gcst_exstd_lib})
list(APPEND gcst_utils_objs gcst_utils_exstd)
gcst_binary_prepare(gcst_utils_exstd)

add_library(gcst_utils STATIC)
gcst_export_prepare(gcst_utils ${gcst_utils_objs})