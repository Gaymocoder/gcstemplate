cmake_minimum_required(VERSION 3.31)
project(gcstemplate VERSION 4.3.0)

find_package(Boost REQUIRED)

block()
    include(${CMAKE_CURRENT_LIST_DIR}/cmake/gcst/utils.cmake)

    set(CMAKE_CXX_STANDARD 23)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)

    set(GCST_INCLUDE_DIRS "${CMAKE_CURRENT_SOURCE_DIR}/include")
    set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/lib)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin)
    
    add_subdirectory(utils)
    add_subdirectory(Hello)
endblock()